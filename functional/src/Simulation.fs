// OptiFolio – Simulation.fs (rev 2)
// ------------------------------------------------------------
// Busca carteiras ótimas via Monte‑Carlo MASSIVAMENTE paralelizado.
// Melhorias:
//   • μ e Σ calculados apenas 1 × por combinação ⇒ 10‑30 × mais rápido
//   • Paralelismo duplo (entre combinações e entre carteiras)
//   • RNG sem contenção: um gerador por thread
//   • MathNet BLAS para algebra vetorial

namespace Functional.Simulation

open System
open System.IO
open Deedle
open MathNet.Numerics
open MathNet.Numerics.Random
open MathNet.Numerics.Distributions
open MathNet.Numerics.LinearAlgebra
open MathNet.Numerics.LinearAlgebra.Double

open Functional.Portfolio.Portfolio

module Simulation =

    // --------------------------------------------------------
    // Utilidades

    /// Gera todas as combinações de tamanho k de um array
    let combinations (k:int) (arr:'T[]) : 'T[][] =
        let rec comb acc start k =
            seq {
                if k = 0 then yield List.rev acc |> List.toArray
                else
                    for i = start to arr.Length - k do
                        yield! comb (arr.[i]::acc) (i+1) (k-1) }
        comb [] 0 k |> Seq.toArray

    /// Sampla vetor da distribuição Dirichlet(alpha=1,…,1)
    let private dirichlet (rng:RandomSource) (k:int) : float[] =
        let gam = Array.init k (fun _ -> Gamma.Sample(rng, 1., 1.))
        let s   = Array.sum gam
        gam |> Array.map (fun g -> g / s)

    /// Sorteia pesos respeitando limite por ativo
    let rec randomWeights (rng:RandomSource) k maxW =
        let w = dirichlet rng k
        if Array.exists (fun x -> x > maxW) w then randomWeights rng k maxW else w

    let toSeries (tickers:string[]) (w:float[]) : Weights =
        Array.zip tickers w |> Series.ofObservations

    [<Literal>]
    let AnnualFactor = 252.

    // --------------------------------------------------------
    // Configuração

    type SimConfig = {
        CombinationSize   : int   // k ativos
        PortfoliosPerComb : int   // quantos vetores de peso por combinação
        MaxWeight         : float // limite individual
        Seed              : int   // seed base
    }

    type SimResult = { 
        Tickers : string[]; 
        Weights : float[];  // Weights of the best portfolio
        Stats : Stats 
    }

    // --------------------------------------------------------
    // Núcleo da simulação para UMA combinação (paralelo interno)

    let private simulateCombination (returns:Frame<DateTime,string>) (cfg:SimConfig) (tickers:string[]) : SimResult =
        // RNG exclusivo desta combinação (thread‑safe)
        let rngRoot = MersenneTwister(cfg.Seed + tickers.GetHashCode())

        // ------ Pré‑cálculo pesado (fechado em 1×) ------
        let sub      = returns.Columns.[tickers]
        let rows     = sub.RowCount
        // Matrix rows×k   (BLAS friendly)
        let m = DenseMatrix.OfArray (Array2D.init rows tickers.Length (fun r c -> sub.[tickers.[c]].GetAt r))
        let muDaily = DenseVector.OfArray (m.ColumnSums().ToArray()) / float rows
        let muAnn = muDaily * AnnualFactor
        // Broadcast mean vector to match matrix dimensions
        let muMatrix = DenseMatrix.OfRows(Array.init rows (fun _ -> muDaily.ToArray()))
        let cen = m - muMatrix
        let sigmaAnn = DenseMatrix.OfArray ((cen.TransposeThisAndMultiply(cen)).ToArray()) / float rows * AnnualFactor

        // Função que avalia UM vetor de peso
        let evaluate (seedAdd:int) =
            let rng = MersenneTwister(cfg.Seed + seedAdd)
            let wArr = randomWeights rng tickers.Length cfg.MaxWeight
            let wVec: DenseVector = DenseVector.OfArray wArr
            let ret  = wVec.DotProduct muAnn
            let vol  = sqrt (wVec * sigmaAnn * wVec)
            let s    = ret / vol
            s, wArr, { AnnualReturn = ret; AnnualVol = vol; Sharpe = s }

        // Paraleliza Monte‑Carlo dentro da combinação
        let bestStat, bestWeights, stats =
            Array.init cfg.PortfoliosPerComb id
            |> Array.Parallel.map evaluate
            |> Array.maxBy (fun (s,_,_) -> s)

        { Tickers = tickers; Weights = bestWeights; Stats = stats }

    // --------------------------------------------------------
    // API principal – duplo paralelismo

    let run (returns:Frame<DateTime,string>) (cfg:SimConfig) : SimResult[] =
        let tickers = returns.ColumnKeys |> Seq.toArray
        let combos  = combinations cfg.CombinationSize tickers

        combos
        |> Array.Parallel.map (simulateCombination returns cfg)
        |> Array.sortByDescending (fun r -> r.Stats.Sharpe)

    /// Salva resultados em CSV (tickers + métricas)
    let saveResults (results:SimResult[]) (path:string) =
        let header = "Tickers,AnnualReturn,AnnualVol,Sharpe"
        let lines  =
            results
            |> Array.map (fun r ->
                let tks  = String.concat "-" r.Tickers
                let st   = r.Stats
                sprintf "%s,%.6f,%.6f,%.6f" tks st.AnnualReturn st.AnnualVol st.Sharpe)
        File.WriteAllLines(path, Array.append [|header|] lines)

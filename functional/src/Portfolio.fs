// OptiFolio – Portfolio.fs
// ------------------------------------------------------------
// Métricas de performance de portfólios.
// Todas as funções são puras e trabalham sobre Frames de retornos
// (log ou simples) já alinhados e sem NaNs.

namespace Functional.Portfolio

open System
open Deedle
open MathNet.Numerics.Statistics

module Portfolio =

    // --------------------------------------------------------
    // Tipos auxiliares

    /// Série de pesos (ticker -> peso); deve somar ~1.0
    type Weights = Series<string,float>

    /// Record com métricas anualizadas
    type Stats = {
        AnnualReturn : float
        AnnualVol    : float
        Sharpe       : float
    }

    // --------------------------------------------------------
    // Helpers internos

    /// Número de pregões por ano (EUA)
    [<Literal>]
    let TradingDays = 252.0

    /// Valida se todos os tickers de pesos estão presentes no Frame
    let private checkCoverage (weights:Weights) (returns:Frame<DateTime,string>) =
        let missing =
            weights.Keys
            |> Seq.filter (fun t -> not (returns.ColumnKeys |> Seq.contains t))
            |> Seq.toList
        match missing with
        | [] -> ()
        | xs -> failwithf "Tickers ausentes nos retornos: %A" xs

    /// Converte Weights Series -> vetor coluna (DenseVector<float>)
    let private toVector (weights:Weights) (orderedTickers:string[]) =
        orderedTickers |> Array.map (fun t -> weights.[t])

    // --------------------------------------------------------
    // Métricas

    /// Média de retorno diário anualizada
    let annualizedReturn (returns:Frame<DateTime,string>) =
        returns.ColumnKeys
        |> Seq.map (fun t -> returns.[t] |> Stats.mean)
        |> Seq.map (fun mu -> mu * TradingDays)  // Simple annualization for daily returns
        |> Seq.toArray
        |> Array.zip (returns.ColumnKeys |> Seq.toArray)
        |> Series.ofObservations

    /// Variância/covariância anualizada (matriz NxN)
    let covMatrixAnnual (returns:Frame<DateTime,string>) : float[,] =
        let data = 
            returns.ColumnKeys
            |> Seq.map (fun t -> returns.[t] |> Series.values |> Seq.toArray)
            |> Seq.toArray
        let cov = Correlation.PearsonMatrix(data)
        // Ajuste para cov real: multiplicar pela var? Usamos diretamente o sample covariance
        let factor = TradingDays
        cov.ToArray() |> Array2D.map (fun c -> c * factor)

    /// Dado um vetor de pesos, calcula return, vol e Sharpe
    let portfolioStats (returns:Frame<DateTime,string>) (weights:Weights) : Stats =
        checkCoverage weights returns
        let tickers = weights.Keys |> Seq.toArray
        let w = toVector weights tickers
        // Filtra frame para os tickers relevantes
        let sub = returns.Columns.[tickers]
        // Vetor de médias diárias
        let mu = sub.ColumnKeys |> Seq.map (fun t -> sub.[t] |> Stats.mean) |> Seq.toArray
        // Cov matrix
        let cov = covMatrixAnnual sub // já anualizada
        let annualR = Array.map2 (fun wi m -> wi * m * TradingDays) w mu |> Array.sum
        // w' Σ w -> anual
        let vol =
            let tmp =
                [| for i in 0 .. w.Length-1 ->
                    [| for j in 0 .. w.Length-1 -> w.[i] * cov.[i,j] * w.[j] |] |> Array.sum |]
                |> Array.sum
            sqrt tmp
        let sharpe = annualR / vol
        { AnnualReturn = annualR; AnnualVol = vol; Sharpe = sharpe }

    /// Retorna função curry para rápida avaliação em otimizações
    let makeEvaluator returns = portfolioStats returns

// OptiFolio – Program.fs
// ------------------------------------------------------------
// Script principal para execução da simulação de carteiras

open System
open System.IO
open Deedle
open Functional.DataLoader
open Functional.Portfolio
open Functional.Simulation

// Função auxiliar para salvar resultados detalhados
let savePortfolioResults (results:Simulation.SimResult[]) (path:string) =
    let header = "Tickers,Weights,AnnualReturn,AnnualVol,Sharpe"
    let lines = 
        results
        |> Array.map (fun r ->
            let tks = String.concat "-" r.Tickers
            let weights = String.concat "-" (Array.map string r.Weights)
            let st = r.Stats
            sprintf "%s,%s,%.6f,%.6f,%.6f" tks weights st.AnnualReturn st.AnnualVol st.Sharpe)
    File.WriteAllLines(path, Array.append [|header|] lines)

// Função auxiliar para salvar métricas de performance
let savePerformanceMetrics (startTime:DateTime) (endTime:DateTime) (results:Simulation.SimResult[]) (path:string) =
    let duration = endTime - startTime
    let header = "Metric,Value"
    let lines = [|
        sprintf "TotalCombinations,%d" results.Length
        sprintf "SimulationTimeSeconds,%.2f" duration.TotalSeconds
        sprintf "CombinationsPerSecond,%.2f" (float results.Length / duration.TotalSeconds)
        sprintf "BestSharpe,%.6f" (results |> Array.maxBy (fun r -> r.Stats.Sharpe) |> fun r -> r.Stats.Sharpe)
        sprintf "WorstSharpe,%.6f" (results |> Array.minBy (fun r -> r.Stats.Sharpe) |> fun r -> r.Stats.Sharpe)
        sprintf "AverageSharpe,%.6f" (results |> Array.averageBy (fun r -> r.Stats.Sharpe))
        sprintf "BestReturn,%.6f" (results |> Array.maxBy (fun r -> r.Stats.AnnualReturn) |> fun r -> r.Stats.AnnualReturn)
        sprintf "WorstReturn,%.6f" (results |> Array.minBy (fun r -> r.Stats.AnnualReturn) |> fun r -> r.Stats.AnnualReturn)
        sprintf "AverageReturn,%.6f" (results |> Array.averageBy (fun r -> r.Stats.AnnualReturn))
        sprintf "BestVolatility,%.6f" (results |> Array.minBy (fun r -> r.Stats.AnnualVol) |> fun r -> r.Stats.AnnualVol)
        sprintf "WorstVolatility,%.6f" (results |> Array.maxBy (fun r -> r.Stats.AnnualVol) |> fun r -> r.Stats.AnnualVol)
        sprintf "AverageVolatility,%.6f" (results |> Array.averageBy (fun r -> r.Stats.AnnualVol))
    |]
    File.WriteAllLines(path, Array.append [|header|] lines)

[<EntryPoint>]
let main argv =
    printfn "Iniciando simulação de carteiras..."
    
    // Carrega e processa dados
    let prices = DataLoader.loadPricesDir("data")
    let simpleRets = DataLoader.simpleReturns prices
    
    // Configura simulação
    let simConfig : Simulation.SimConfig = {
        CombinationSize = 25        // 25 das 30 empresas
        PortfoliosPerComb = 1000    // 1000 carteiras por combinação
        MaxWeight = 0.20           // máximo 20% por ativo
        Seed = 42                  // seed fixa para reprodutibilidade
    }
    
    // Executa simulação
    printfn "Executando simulação com %d combinações..." (Simulation.combinations simConfig.CombinationSize (simpleRets.ColumnKeys |> Seq.toArray)).Length
    let startTime = DateTime.Now
    let results = Simulation.run simpleRets simConfig
    let endTime = DateTime.Now
    let duration = endTime - startTime
    
    // Salva resultados
    let portfolioPath = "portfolio_results.csv"
    let performancePath = "performance_results.csv"
    
    savePortfolioResults results portfolioPath
    savePerformanceMetrics startTime endTime results performancePath
    
    // Resumo final
    printfn "\nSimulação concluída em %.2f segundos" duration.TotalSeconds
    printfn "Resultados salvos em:"
    printfn "  - %s" portfolioPath
    printfn "  - %s" performancePath
    
    let bestPortfolio = results |> Array.maxBy (fun r -> r.Stats.Sharpe)
    printfn "\nMelhor carteira encontrada:"
    printfn "  Sharpe Ratio: %.4f" bestPortfolio.Stats.Sharpe
    printfn "  Retorno Anual: %.2f%%" (bestPortfolio.Stats.AnnualReturn * 100.0)
    printfn "  Volatilidade Anual: %.2f%%" (bestPortfolio.Stats.AnnualVol * 100.0)
    printfn "  Ativos: %s" (String.concat ", " bestPortfolio.Tickers)
    
    0 // retorna um código de saída inteiro



// OptiFolio – DataLoader.fs (rev. 3)
// ------------------------------------------------------------
// Lê arquivos CSV de PREÇOS já baixados (um por ticker) e
// localizados em `src/data/`.
// Cada CSV tem exatamente duas colunas:
//     Date,<TICKER>
// onde <TICKER> é igual ao nome do arquivo (AAPL.csv → AAPL).
// Resultado: Frame<DateTime,string> com colunas por ticker.
// Funções auxiliares calculam retornos logarítmicos.

namespace Functional.DataLoader

open System
open System.IO
open Deedle

module DataLoader =

    /// Alias para o Frame de preços diários
    type PriceFrame = Frame<DateTime, string>

    /// Lê um único CSV de preços e o devolve como um Frame com 1 coluna
    let private loadSingleCsv (filePath:string) : PriceFrame =
        let ticker = Path.GetFileNameWithoutExtension filePath |> fun s -> s.ToUpperInvariant()
        // Lê, indexa pela coluna "Date", seleciona a coluna do ticker
        Frame.ReadCsv(filePath, hasHeaders=true, inferTypes=true)
        |> Frame.indexRowsDate "Date"
        |> fun f -> f.GetColumn<float>(ticker)              // Series<DateTime,float>
        |> Series.mapKeys (fun d -> d.Date)                 // normaliza horário se houver
        |> fun s -> Frame.ofColumns [ ticker, s ]           // Frame c/ uma única coluna

    /// Carrega todos os CSVs de um diretório, mesclando por data.
    let loadPricesDir (dirPath:string) : PriceFrame =
        Directory.GetFiles(dirPath, "*.csv")
        |> Array.map loadSingleCsv
        |> Frame.mergeAll
        |> Frame.sortRowsByKey

    /// Carrega dados de preços de ações a partir de arquivos CSV
    let loadPrices (path: string) : PriceFrame =
        let files = Directory.GetFiles(path, "*.csv")
        
        let frames = 
            files
            |> Array.map (fun file ->
                let ticker = Path.GetFileNameWithoutExtension(file)
                let frame = Frame.ReadCsv(file)
                frame
                    .IndexRows<DateTime>("Date")
                    .GetColumn<float>("Close")
                    |> fun s -> Frame.ofColumns [ticker, s])
        
        // Combina todas as séries em um único Frame
        frames
        |> Array.reduce (fun acc frame -> Frame.merge acc frame)
        |> Frame.sortRowsByKey

    /// Calcula retornos simples (preço atual / preço anterior - 1)
    let simpleReturns (prices: PriceFrame) : PriceFrame =
        prices
        |> Frame.mapCols (fun _ col ->
            let s = col |> Series.mapValues (fun x -> x :?> float)
            s / (s |> Series.shift 1) - 1.0)
        |> Frame.dropSparseRows

    /// Carrega dados de backtest a partir de arquivos CSV
    let loadBacktestData (path: string) : PriceFrame =
        loadPrices path

    // ------------------------------------------------------------
    // Derivados

    /// Converte preços para retornos logarítmicos diários Δln(P)
    let logReturns (prices:PriceFrame) : PriceFrame =
        prices
        |> Frame.mapValues (fun x -> log x)
        |> Frame.diff 1
        |> Frame.dropSparseRows

    /// Série acumulada de valor (valor inicial 1.0) a partir de retornos simples
    let cumulative (returns:PriceFrame) : PriceFrame =
        let cumulativeSeries = 
            returns
            |> Frame.mapValues (fun r -> 1.0 + r)
            |> Frame.mapRows (fun _ row -> 
                row 
                |> Series.values 
                |> Seq.cast<float>
                |> Seq.fold (*) 1.0)
        Frame.ofColumns [ "Cumulative", cumulativeSeries ]

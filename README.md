# OptiFolio

Portfolio Optimizer em **F#** e **Python** focado em desempenho.  
Carrega preços históricos, calcula retornos, simula centenas de milhares
de carteiras em paralelo e produz a que maximiza o **Sharpe ratio**.

O projeto é composto por duas partes:
- **F#**: código funcional e focado em desempenho.
- **Python**: código para baixar os dados de preços das ações.

O projeto também inclui os scripts de simulação em Python, porém não foram testados. Apenas o módulo funcional em F# foi testado.

---

## 1 · Requisitos

| Software                 | Versão mínima | Observações                                 |
|--------------------------|---------------|---------------------------------------------|
| **.NET SDK**            | **8.0 LTS**   | macOS (arm64 / x64), Windows ou Linux       |
| **F#** (via SDK)        | 8.0           | Não é preciso instalar nada extra           |
| **Git**                 | 2.x           | Para clonar o repositório                   |

> **macOS** – instale o .NET com Homebrew  
> `brew install --cask dotnet-sdk`

> **Ubuntu** – script oficial  
> ```bash
> wget https://dot.net/v1/dotnet-install.sh
> chmod +x dotnet-install.sh
> ./dotnet-install.sh --channel 8.0
> ```

---

## 2 · Instalação

```bash
# 1. Clone o projeto
git clone https://github.com/thomaschiari/optifolio.git
cd optifolio/functional/src

# 2. Restaure dependências (Deedle + MathNet)
dotnet restore
```

> As dependências são definidas no arquivo `functional/functional.fsproj`
> e serão baixadas automaticamente (`Deedle`, `MathNet.Numerics`,
> `MathNet.Numerics.FSharp`).

---

## 3 · Preparar os dados (opcional)

Os dados de preços de ações já estão disponíveis no repositório, mas caso queira baixar os dados novamente, é possível fazer isso com o script [functional/utils/data_loading.py](https://github.com/thomaschiari/optifolio/blob/main/functional/utils/data_loading.py). É possível alterar as datas para simular diferentes períodos. Essa etapa é opcional, pois os dados já estão disponíveis no repositório.

Para rodar o script, siga os passos abaixo:

1. **Abra** um novo terminal na raiz do projeto e **instale** as dependências do Python

   ```bash
   pip install -r requirements.txt
   ```

2. **Navegue** até o diretório `functional/utils` e **execute** o script

   ```bash
   cd functional/utils && python data_loading.py
   ```  

---

## 4 · Como executar

### Execução padrão (modo Release + paralelismo)

```bash
dotnet build -c Release && dotnet run -c Release
```

*Outputs* gerados na pasta `functional/src`:

| Arquivo                   | Descrição                                   |
| ------------------------- | ------------------------------------------- |
| `portfolio_results.csv`   | Cada linha = melhor carteira por combinação |
| `performance_results.csv` | Métricas globais da simulação               |

### Backtesting Q1 2025 (opcional)

Para testar a carteira otimizada no primeiro trimestre de 2025 vá para a raiz do projeto e execute o script (opcional, pois os dados já estão disponíveis no repositório):

```bash
cd functional/utils
python test_q1_2025.py
```

As bibliotecas necessárias para executar o script já foram instaladas no passo 2 da instalação. Se não estiverem instaladas, instale-as com o comando:

```bash
pip install -r requirements.txt
```

*Output* gerado:
| Arquivo                   | Descrição                                   |
| ------------------------- | ------------------------------------------- |
| `backtesting_results.csv` | Comparativo Q4 2024 vs Q1 2025              |

---

## 5 · Resultados obtidos

### 5.1 · Desempenho (MacBook Air M3)

| Métrica | Valor |
|---------|-------|
| Total de Combinações | 142,506 |
| Tempo de Simulação | 464.53 segundos |
| Combinações/segundo | 306.78 |

### 5.2 · Melhor carteira (exemplo)

A melhor carteira encontrada teve as seguintes características:

| Métrica | Valor |
|---------|-------|
| Sharpe Ratio | 3.23 |
| Retorno Anual | 40.11% |
| Volatilidade Anual | 12.40% |

#### Resumo das Métricas

| Métrica | Melhor | Média | Pior |
|---------|--------|-------|------|
| Sharpe Ratio | 3.23 | 2.66 | 1.76 |
| Retorno Anual | 44.28% | 33.64% | 21.82% |
| Volatilidade Anual | 9.98% | 12.69% | 18.22% |

#### Top 5 Carteiras

| Rank | Sharpe | Retorno | Vol | Ativos |
|------|--------|---------|-----|---------|
| 1 | 3.23 | 40.11% | 12.40% | CSCO, V, PG, MCD, AMZN, MMM, KO, MSFT, NVDA, HD, AXP, CVX, NKE, IBM, GS, DIS, JPM, VZ, UNH, HON, AAPL, WMT, TRV, JNJ, CRM |
| 2 | 3.23 | 40.04% | 12.40% | CSCO, V, PG, MCD, AMZN, MMM, KO, SHW, NVDA, HD, AXP, CVX, NKE, IBM, GS, DIS, JPM, VZ, UNH, HON, AAPL, WMT, TRV, JNJ, CRM |
| 3 | 3.23 | 40.04% | 12.40% | CSCO, V, PG, MCD, AMZN, MMM, MSFT, SHW, NVDA, HD, AXP, CVX, NKE, IBM, GS, DIS, JPM, VZ, UNH, HON, AAPL, WMT, TRV, JNJ, CRM |
| 4 | 3.23 | 40.06% | 12.41% | CSCO, V, PG, MCD, AMZN, MMM, KO, MSFT, NVDA, HD, AXP, CVX, NKE, IBM, GS, DIS, JPM, AMGN, UNH, HON, AAPL, WMT, TRV, JNJ, CRM |
| 5 | 3.23 | 39.96% | 12.37% | CSCO, V, PG, MCD, AMZN, KO, MSFT, SHW, NVDA, HD, AXP, CVX, NKE, IBM, GS, DIS, JPM, VZ, UNH, HON, AAPL, WMT, TRV, JNJ, CRM |

### 5.3 · Backtesting Q1 2025

A carteira otimizada para Q4 2024 foi testada no primeiro trimestre de 2025:

| Período | Retorno Anual | Volatilidade | Sharpe |
|---------|---------------|--------------|---------|
| Q4 2024 | 40.11% | 12.40% | 3.23 |
| Q1 2025 | -14.29% | 15.37% | -0.93 |

Como pode ser visto, a carteira otimizada para Q4 2024 não performou bem no primeiro trimestre de 2025.

> **Nota**: Os pesos de cada ativo podem ser encontrados no arquivo `portfolio_results.csv`. A simulação foi executada com 25 ativos por carteira, selecionados entre os 30 ativos disponíveis.

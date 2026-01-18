import numpy as np
import pandas as pd

class ENEMDataLoader:
    """
    Carregador de dados do ENEM.
    Em produção, carregaria dados reais do INEP.
    Por enquanto, gera dados simulados realistas.
    """
    
    @staticmethod
    def gerar_parametros_realistas(num_itens=180, seed=None):
        """
        Gera parâmetros realistas para questões do ENEM.
        
        Args:
            num_itens: Número de questões (padrão: 180 para ENEM completo)
            seed: Seed para reprodutibilidade
        
        Returns:
            DataFrame com colunas: item_id, a, b, c
        """
        if seed:
            np.random.seed(seed)
        
        # Parâmetros realistas baseados em análises do ENEM
        # Discriminação (a): maioria entre 1.0 e 2.0
        a = np.random.normal(1.4, 0.4, num_itens)
        a = np.clip(a, 0.5, 3.0)  # Limitar entre 0.5 e 3.0
        
        # Dificuldade (b): distribuição normal centrada em 0
        b = np.random.normal(0, 1.2, num_itens)
        b = np.clip(b, -3, 3)  # Limitar entre -3 e 3
        
        # Acerto casual (c): entre 0.15 e 0.25 (4 alternativas)
        c = np.random.uniform(0.15, 0.25, num_itens)
        
        df = pd.DataFrame({
            'item_id': range(1, num_itens + 1),
            'a': a,
            'b': b,
            'c': c
        })
        
        return df
    
    @staticmethod
    def carregar_csv(caminho):
        """
        Carrega parâmetros de um arquivo CSV.
        
        Esperado: colunas 'a', 'b', 'c' (ou 'discriminacao', 'dificuldade', 'acerto_casual')
        """
        df = pd.read_csv(caminho)
        
        # Renomear colunas se necessário
        mapeamento = {
            'discriminacao': 'a',
            'dificuldade': 'b',
            'acerto_casual': 'c'
        }
        df = df.rename(columns=mapeamento)
        
        # Validar colunas necessárias
        colunas_necessarias = ['a', 'b', 'c']
        if not all(col in df.columns for col in colunas_necessarias):
            raise ValueError(f"CSV deve conter as colunas: {colunas_necessarias}")
        
        return df[colunas_necessarias]
    
    @staticmethod
    def gerar_exemplo_aluno_coerente(num_itens=45):
        """
        Gera exemplo de respostas coerentes (acerta fáceis, erra difíceis).
        """
        # Gerar parâmetros
        np.random.seed(42)
        params = ENEMDataLoader.gerar_parametros_realistas(num_itens, seed=42)
        
        # Simular respostas coerentes com theta = 0.5
        theta_aluno = 0.5
        respostas = []
        
        for _, row in params.iterrows():
            # Probabilidade de acerto baseada no 3PL
            p = row['c'] + (1 - row['c']) / (1 + np.exp(-row['a'] * (theta_aluno - row['b'])))
            resposta = 1 if np.random.random() < p else 0
            respostas.append(resposta)
        
        return np.array(respostas), params
    
    @staticmethod
    def gerar_exemplo_aluno_incoerente(num_itens=45):
        """
        Gera exemplo de respostas incoerentes (erra fáceis, acerta difíceis).
        """
        np.random.seed(42)
        params = ENEMDataLoader.gerar_parametros_realistas(num_itens, seed=42)
        
        # Respostas aleatórias (simula chute)
        respostas = np.random.randint(0, 2, num_itens)
        
        return respostas, params

if __name__ == "__main__":
    # Teste
    loader = ENEMDataLoader()
    
    # Gerar parâmetros realistas
    params = loader.gerar_parametros_realistas(10)
    print("Parâmetros Realistas:")
    print(params)
    print()
    
    # Gerar exemplo coerente
    respostas_coe, params_coe = loader.gerar_exemplo_aluno_coerente(10)
    print("Respostas Coerentes:", respostas_coe)
    print()
    
    # Gerar exemplo incoerente
    respostas_incoe, params_incoe = loader.gerar_exemplo_aluno_incoerente(10)
    print("Respostas Incoerentes:", respostas_incoe)

import numpy as np
from scipy.optimize import minimize

class TRIEngine:
    """
    Motor de cálculo para Teoria de Resposta ao Item (TRI) baseado no modelo 3PL.
    Utilizado para estimar a proficiência (theta) de estudantes no ENEM.
    """
    
    def __init__(self, mean_scale=500, std_scale=100):
        self.mean_scale = mean_scale
        self.std_scale = std_scale

    def logistic_3pl(self, theta, a, b, c):
        """
        Modelo Logístico de 3 Parâmetros (3PL).
        P(theta) = c + (1 - c) / (1 + exp(-a * (theta - b)))
        """
        return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

    def log_posterior(self, theta, responses, params_a, params_b, params_c):
        """
        Calcula a log-posterior (Verossimilhança + Prior Normal).
        Prior: Normal(0, 1) - assume que a maioria dos alunos está perto da média.
        """
        p = self.logistic_3pl(theta, params_a, params_b, params_c)
        p = np.clip(p, 1e-10, 1 - 1e-10)
        
        # Log-verossimilhança
        log_l = np.sum(responses * np.log(p) + (1 - responses) * np.log(1 - p))
        
        # Log-prior (Normal(0, 1))
        log_prior = -0.5 * (theta**2)
        
        return log_l + log_prior

    def estimate_theta(self, responses, params_a, params_b, params_c):
        """
        Estima o theta (proficiência) usando Máxima A Posteriori (MAP).
        """
        objective = lambda t: -self.log_posterior(t, responses, params_a, params_b, params_c)
        initial_theta = 0.0
        result = minimize(objective, initial_theta, method='BFGS')
        return result.x[0] if result.success else initial_theta

    def to_enem_score(self, theta):
        """
        Converte o theta para a escala ENEM (Média 500, DP 100).
        Nota: No ENEM real, cada área tem constantes de transformação específicas.
        """
        return self.mean_scale + (self.std_scale * theta)

    def analyze_consistency(self, theta, responses, params_b):
        """
        Analisa a consistência pedagógica (Coerência da TRI).
        Verifica se o aluno acertou questões difíceis e errou fáceis.
        """
        # Ordenar itens por dificuldade (parâmetro b)
        sorted_indices = np.argsort(params_b)
        sorted_responses = responses[sorted_indices]
        sorted_diffs = params_b[sorted_indices]
        
        # Um aluno coerente deve ter acertos concentrados nas questões com b < theta
        # e erros nas questões com b > theta.
        
        analysis = {
            "total_acertos": int(np.sum(responses)),
            "theta_estimado": round(theta, 4),
            "coerencia": "Alta" if self._check_coherence(theta, responses, params_b) else "Baixa"
        }
        return analysis

    def _check_coherence(self, theta, responses, params_b):
        # Simplificação: se o aluno erra muitas questões fáceis (b << theta), a coerência é baixa
        easy_items_mask = params_b < (theta - 1.0)
        if np.any(easy_items_mask):
            easy_responses = responses[easy_items_mask]
            accuracy_easy = np.mean(easy_responses)
            if accuracy_easy < 0.5: # Errou mais da metade das fáceis
                return False
        return True

# Exemplo de uso
if __name__ == "__main__":
    # Simulação de 10 itens
    a = np.array([1.5, 1.2, 1.8, 1.0, 2.0, 1.4, 1.6, 1.1, 1.9, 1.3]) # Discriminação
    b = np.array([-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5]) # Dificuldade
    c = np.array([0.2] * 10) # Acerto casual (chute)
    
    # Respostas de um aluno (1 = acerto, 0 = erro)
    # Aluno coerente: acerta as fáceis, erra as difíceis
    respostas_coerentes = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    
    # Aluno incoerente: erra as fáceis, acerta as difíceis (chute)
    respostas_incoerentes = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
    
    engine = TRIEngine()
    
    theta_c = engine.estimate_theta(respostas_coerentes, a, b, c)
    nota_c = engine.to_enem_score(theta_c)
    
    theta_i = engine.estimate_theta(respostas_incoerentes, a, b, c)
    nota_i = engine.to_enem_score(theta_i)
    
    print(f"Aluno Coerente - Theta: {theta_c:.2f}, Nota ENEM: {nota_c:.2f}")
    print(f"Aluno Incoerente - Theta: {theta_i:.2f}, Nota ENEM: {nota_i:.2f}")

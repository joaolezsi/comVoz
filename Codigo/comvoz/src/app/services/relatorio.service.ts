import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';

interface EstatisticasResumo {
  pesquisas_ativas: number;
  respostas_recebidas: number;
  taxa_resposta: number;
  score: number;
}

interface EstatisticasPesquisa {
  respostas: number;
  taxaConversao: number;
  respostasPorAlternativa: any[];
  distribuicaoRespostas: any[];
}

@Injectable({
  providedIn: 'root'
})
export class RelatorioService {
  private apiUrl = 'http://127.0.0.1:8080';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  // Obtém resumo geral de estatísticas (para o dashboard)
  getEstatisticasResumo(): Observable<EstatisticasResumo> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get<EstatisticasResumo>(`${this.apiUrl}/dashboard`, { headers })
        .pipe(
          catchError(error => {
            console.error('Erro ao carregar estatísticas:', error);
            // Retorna dados fictícios como fallback
            return of({
              pesquisas_ativas: 2,
              respostas_recebidas: 34,
              taxa_resposta: 68,
              score: 75
            });
          })
        );
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return of({
        pesquisas_ativas: 1,
        respostas_recebidas: 10,
        taxa_resposta: 50,
        score: 60
      });
    }
  }

  // Obtém estatísticas detalhadas de uma pesquisa específica
  getEstatisticasPesquisa(pesquisaId: string | number): Observable<EstatisticasPesquisa> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get<EstatisticasPesquisa>(`${this.apiUrl}/pesquisas/${pesquisaId}/estatisticas`, { headers })
        .pipe(
          catchError(error => {
            console.error(`Erro ao carregar estatísticas da pesquisa ${pesquisaId}:`, error);
            // Retorna dados fictícios como fallback
            return of({
              respostas: 15,
              taxaConversao: 60,
              respostasPorAlternativa: [],
              distribuicaoRespostas: []
            });
          })
        );
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return of({
        respostas: 0,
        taxaConversao: 0,
        respostasPorAlternativa: [],
        distribuicaoRespostas: []
      });
    }
  }

  // Gera relatório em formato PDF
  gerarRelatorioPDF(pesquisaId: string | number): Observable<Blob> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get(`${this.apiUrl}/relatorio/${pesquisaId}`, { 
        headers,
        responseType: 'blob'
      });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      throw error;
    }
  }
} 
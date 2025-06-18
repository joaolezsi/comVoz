import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

interface PlanoLimites {
  questoes: number;
  envios: number;
}

interface PlanoRecursos {
  disparo: boolean;
  qrcode: boolean;
  relatorio: boolean;
  reuniao: boolean;
  comparacao: boolean;
}

export interface Plano {
  id: number;
  nome: string;
  preco: number;
  limite_pesquisas: number;
  descricao: string;
  limites?: PlanoLimites;
  recursos?: PlanoRecursos;
}

export interface PlanoChangeRequest {
  id: number;
  empresa: {
    id: number;
    nome: string;
    cnpj: string;
  };
  planoAtual: Plano;
  planoDesejado: Plano;
  status: 'pending' | 'approved' | 'rejected';
  dataSolicitacao: string;
}

@Injectable({
  providedIn: 'root'
})
export class PlanoService {
  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  getPlanos(): Observable<Plano[]> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get<Plano[]>(`${this.apiUrl}/plans`, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      // Continuamos com a requisição sem headers para manter compatibilidade em caso de erro
      return this.http.get<Plano[]>(`${this.apiUrl}/plans`);
    }
  }

  getPlanoById(planoId: number): Observable<Plano> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get<Plano>(`${this.apiUrl}/plan/${planoId}`, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return this.http.get<Plano>(`${this.apiUrl}/plan/${planoId}`);
    }
  }

  getPlanoUsuario(userId: number): Observable<Plano> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get<Plano>(`${this.apiUrl}/plans/get_user_plan/${userId}`, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return this.http.get<Plano>(`${this.apiUrl}/plans/get_user_plan/${userId}`);
    }
  }

  getPlanosInteresse(userId: number): Observable<Plano[]> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get<Plano[]>(`${this.apiUrl}/plans/get_user_interests/${userId}`, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return this.http.get<Plano[]>(`${this.apiUrl}/plans/get_user_interests/${userId}`);
    }
  }

  registrarInteresse(planId: number, userId: number): Observable<any> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.post<any>(`${this.apiUrl}/plans/registrar_interesse`, {
        plan_id: planId,
        user_id: userId
      }, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return this.http.post<any>(`${this.apiUrl}/plans/registrar_interesse`, {
        plan_id: planId,
        user_id: userId
      });
    }
  }

  atualizarPlanoUsuario(planId: number, userId: number): Observable<any> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.post<any>(`${this.apiUrl}/subscribe_plan`, {
        plan_id: planId,
        user_id: userId
      }, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return this.http.post<any>(`${this.apiUrl}/subscribe_plan`, {
        plan_id: planId,
        user_id: userId
      });
    }
  }

  getPlanChangeRequests(): Observable<PlanoChangeRequest[]> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.get<PlanoChangeRequest[]>(`${this.apiUrl}/plans/change-requests`, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return this.http.get<PlanoChangeRequest[]>(`${this.apiUrl}/plans/change-requests`);
    }
  }

  respondToPlanChangeRequest(requestId: number, approved: boolean): Observable<any> {
    try {
      const headers = this.authService.getAuthHeaders();
      return this.http.post<any>(`${this.apiUrl}/plans/change-requests/${requestId}/respond`, {
        approved
      }, { headers });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      return this.http.post<any>(`${this.apiUrl}/plans/change-requests/${requestId}/respond`, {
        approved
      });
    }
  }
}

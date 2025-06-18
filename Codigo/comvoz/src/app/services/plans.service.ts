import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

export interface TrocaPlano {
  id: number;
  interest_date: string;
  notes: string;
  plan: {
    id: number;
    name: string;
    description: string;
    price: number;
  };
  plan_id: number;
  status: 'pendente' | 'aprovado' | 'rejeitado' | 'atendido';
  user: {
    id: number;
    name: string;
    email: string;
    cnpj: string;
  };
  user_id: number;
}

@Injectable({
  providedIn: 'root'
})
export class PlansService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient, private authService: AuthService) { }

  getAllInterests(): Observable<TrocaPlano[]> {
    const headers = this.authService.getAuthHeaders();
    return this.http.get<TrocaPlano[]>(`${this.apiUrl}/plans/get_all_interesses`, { headers });
  }

  responderSolicitacao(interestId: number, planId: number, userId: number): Observable<any> {
    const authHeaders = this.authService.getAuthHeaders();
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': authHeaders.get('Authorization') || ''
    });

    const body = {
      plan_id: parseInt(planId.toString(), 10),
      user_id: parseInt(userId.toString(), 10),
      interest_id: parseInt(interestId.toString(), 10)
    };

    console.log('=== DEBUG REQUISIÇÃO PLANS SERVICE ===');
    console.log('URL da requisição:', `${this.apiUrl}/plans/subscribe_plan`);
    console.log('Headers:', headers);
    console.log('Body enviado:', body);
    console.log('Token Bearer:', authHeaders.get('Authorization'));
    console.log('=====================================');

    return this.http.post(`${this.apiUrl}/plans/subscribe_plan`, body, { headers });
  }
} 
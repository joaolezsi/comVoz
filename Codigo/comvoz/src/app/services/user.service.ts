import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface UserProfile {
  id: number;
  nome_completo: string;
  email: string;
  telefone: string;
  empresa: string;
  cargo: string;
  cnpj: string;
  is_admin: boolean;
  plano_contratado?: any;
}

export interface UpdateProfileData {
  nome_completo?: string;
  telefone?: string;
  empresa?: string;
  cargo?: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { 
    console.log('UserService inicializado com API URL:', this.apiUrl);
  }

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    console.log('Token para requisição:', token ? 'Token presente' : 'Token ausente');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  private handleError(error: HttpErrorResponse) {
    console.error('Erro HTTP detalhado:', error);
    let errorMessage = '';
    
    if (error.error instanceof ErrorEvent) {
      // Erro do lado do cliente
      errorMessage = `Erro: ${error.error.message}`;
    } else {
      // Erro do lado do servidor
      errorMessage = `Erro ${error.status}: ${error.message}`;
      console.error('Status:', error.status);
      console.error('Body:', error.error);
      console.error('Headers:', error.headers);
    }
    
    return throwError(() => error);
  }

  /**
   * Obtém o perfil completo do usuário atual
   */
  getUserProfile(): Observable<UserProfile> {
    const headers = this.getAuthHeaders();
    const url = `${this.apiUrl}/usuarios/perfil`;
    
    console.log('Fazendo requisição GET para:', url);
    console.log('Headers:', headers.keys());
    
    return this.http.get<UserProfile>(url, { headers }).pipe(
      tap(response => console.log('Resposta GET perfil:', response)),
      catchError(this.handleError.bind(this))
    );
  }

  /**
   * Atualiza o perfil do usuário
   */
  updateUserProfile(profileData: UpdateProfileData): Observable<any> {
    const headers = this.getAuthHeaders();
    const url = `${this.apiUrl}/usuarios/perfil`;
    
    console.log('Fazendo requisição PUT para:', url);
    console.log('Dados a enviar:', profileData);
    console.log('Headers:', headers.keys());
    
    return this.http.put(url, profileData, { headers }).pipe(
      tap(response => console.log('Resposta PUT perfil:', response)),
      catchError(this.handleError.bind(this))
    );
  }
} 
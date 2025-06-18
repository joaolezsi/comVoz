import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

interface User {
  id: number;
  nome_completo: string;
  email: string;
  cargo?: string;
  cnpj?: string;
  empresa?: string;
  telefone?: string;
  plano_contratado?: any;
  token: string;
  is_admin?: boolean;
}

interface JWTPayload {
  sub: string;
  is_admin: boolean;
  email: string;
  nome: string;
  exp: number;
  iat: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8080';
  private currentUser: User | null = null;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Tenta recuperar o usuário do localStorage ao inicializar o serviço
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        this.currentUser = JSON.parse(userData);
      } catch (e) {
        console.error('Erro ao processar dados do usuário:', e);
        this.currentUser = null;
      }
    }
  }

  /**
   * Decodifica um token JWT sem verificar a assinatura
   * @param token Token JWT
   * @returns Payload decodificado ou null se inválido
   */
  private decodeJWT(token: string): JWTPayload | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        return null;
      }

      const payload = parts[1];
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(decoded);
    } catch (error) {
      console.error('Erro ao decodificar JWT:', error);
      return null;
    }
  }

  /**
   * Verifica se o token JWT ainda é válido
   * @param token Token JWT
   * @returns true se válido, false caso contrário
   */
  private isTokenValid(token: string): boolean {
    const payload = this.decodeJWT(token);
    if (!payload) {
      return false;
    }

    const now = Math.floor(Date.now() / 1000);
    return payload.exp > now;
  }

  /**
   * Verifica se o usuário atual é administrador
   * @returns true se for admin, false caso contrário
   */
  isAdmin(): boolean {
    const token = localStorage.getItem('token');
    if (!token || !this.isTokenValid(token)) {
      return false;
    }

    const payload = this.decodeJWT(token);
    return payload?.is_admin || false;
  }

  /**
   * Obtém informações do usuário a partir do token JWT
   * @returns Informações do usuário ou null se inválido
   */
  getUserFromToken(): JWTPayload | null {
    const token = localStorage.getItem('token');
    if (!token || !this.isTokenValid(token)) {
      return null;
    }

    return this.decodeJWT(token);
  }

  login(email: string, password: string): Observable<any> {
    // Criar cabeçalho de autenticação Basic
    const headers = new HttpHeaders({
      'Authorization': 'Basic ' + btoa(email + ':' + password)
    });

    // Fazer requisição GET para a rota de login com Basic Auth
    return this.http.get<User>(`${this.apiUrl}/usuarios/login`, { headers })
      .pipe(
        tap(user => {
          // Armazenar dados do usuário e token JWT
          this.currentUser = user;
          
          // Adicionar informação de admin ao usuário baseado no token
          const payload = this.decodeJWT(user.token);
          if (payload) {
            user.is_admin = payload.is_admin;
          }
          
          localStorage.setItem('user', JSON.stringify(user));
          localStorage.setItem('token', user.token);
        }),
        catchError(error => {
          console.error('Erro ao fazer login:', error);
          throw error;
        })
      );
  }

  logout(): void {
    this.currentUser = null;
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }

  getCurrentUser(): User | null {
    return this.currentUser;
  }

  isLoggedIn(): boolean {
    const token = localStorage.getItem('token');
    return !!this.currentUser && !!token && this.isTokenValid(token);
  }

  getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token de autenticação não encontrado');
    }
    
    if (!this.isTokenValid(token)) {
      this.logout();
      throw new Error('Token de autenticação expirado');
    }
    
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  /**
   * Atualiza os dados do usuário no localStorage e na memória
   * @param userData Dados atualizados do usuário
   */
  updateUserData(userData: any): void {
    if (this.currentUser) {
      // Mantém o token existente
      const token = this.currentUser.token;
      
      // Atualiza os dados do usuário
      this.currentUser = {
        ...userData,
        token: token
      };
      
      // Atualiza no localStorage
      localStorage.setItem('user', JSON.stringify(this.currentUser));
    }
  }
} 
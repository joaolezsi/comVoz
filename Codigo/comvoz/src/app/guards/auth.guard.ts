import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): boolean {
    // Verificar se o usuário está autenticado
    const isAuthenticated = localStorage.getItem('user') !== null;
    
    if (!isAuthenticated) {
      // Se não estiver autenticado, redireciona para login
      this.router.navigate(['/login']);
      return false;
    }
    
    return true;
  }
} 
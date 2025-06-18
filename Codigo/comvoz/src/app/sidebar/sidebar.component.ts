import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

interface User {
  id: number;
  nome_completo: string;
  email: string;
  cargo?: string;
}

interface MenuItem {
  label: string;
  icon: string;
  route?: string;
  subItems?: MenuItem[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  @Output() itemSelected = new EventEmitter<MenuItem>();
  isCollapsed = false;
  expandedMenu: string | null = null;
  userName = 'Usuário';
  userRole = 'Cliente';
  currentUser: User | null = null;
  isAdmin = false;

  menuItems: MenuItem[] = [
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Pesquisas', icon: 'search', route: '/pesquisas' },
    { label: 'Criar questões', icon: 'add_circle', route: '/questoes' },
    { label: 'Contatos', icon: 'contacts', route: '/contatos' },
    { label: 'Planos', icon: 'card_membership', route: '/planos' },
    { label: 'Admin Planos', icon: 'admin_panel_settings', route: '/admin/planos' },
    { label: 'Configurações', icon: 'settings', route: '/configuracoes' }
  ];

  constructor(
    public router: Router,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.loadUserData();
  }

  loadUserData() {
    this.currentUser = this.authService.getCurrentUser();
    
    if (this.currentUser) {
      this.userName = this.currentUser.nome_completo || 'Usuário';
      this.userRole = this.currentUser.cargo || 'Cliente';
      // Usar o método isAdmin() do AuthService que verifica o JWT
      this.isAdmin = this.authService.isAdmin();
    } else {
      // Se não conseguir obter o usuário do AuthService, tenta do localStorage
      try {
        const userData = localStorage.getItem('user');
        if (userData) {
          this.currentUser = JSON.parse(userData);
          this.userName = this.currentUser?.nome_completo || 'Usuário';
          this.userRole = this.currentUser?.cargo || 'Cliente';
          // Usar o método isAdmin() do AuthService que verifica o JWT
          this.isAdmin = this.authService.isAdmin();
        }
      } catch (error) {
        console.error('Erro ao carregar dados do usuário:', error);
        // Valores padrão já definidos
      }
    }

    // Se não houver usuário logado, redireciona para a tela de login
    if (!this.currentUser && !localStorage.getItem('user')) {
      this.router.navigate(['/login']);
    }
  }

  selectItem(item: any, event?: MouseEvent) {
    if (event) {
      event.stopPropagation(); // Previne que o clique propague para o item pai
    }

    if (item.subItems) {
      // Expande ou recolhe o menu com subitens
      this.expandedMenu = this.expandedMenu === item.label ? null : item.label;
    } else {
      this.itemSelected.emit(item);
      
      if (item.route) {
        this.router.navigate([item.route]);
      }
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  navigateTo(route: string) {
    this.router.navigate([route]);
  }

  isActive(route: string): boolean {
    return this.router.url === route;
  }
}
import { Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { WithSidebarLayout } from './layouts/with-sidebar.layout';
import { WithoutSidebarLayout } from './layouts/without-sidebar.layout';
import { NotificationComponent } from './notification/notification.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, WithSidebarLayout, WithoutSidebarLayout, NotificationComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(public router: Router) {}

  shouldShowSidebar(): boolean {
    const currentRoute = this.router.url;
    // Lista de rotas que não devem mostrar a sidebar
    const publicRoutes = ['/login', '/cadastrar', '/home', '/responder'];
    return !publicRoutes.some(route => currentRoute.startsWith(route));
  }

}
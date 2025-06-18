import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { CadastroComponent } from './cadastro/cadastro.component';
import { HomeComponent } from './home/home.component';
import { QuestoesComponent } from './questoes/questoes.component';
import { PlanosComponent } from './planos/planos.component';
import { PesquisasComponent } from './pesquisas/pesquisas.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { RelatoriosComponent } from './relatorios/relatorios.component';
import { ContatosComponent } from './contatos/contatos.component';
import { ConfiguracoesComponent } from './configuracoes/configuracoes.component';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';
import { AdminPlanosComponent } from './admin/admin-planos/admin-planos.component';
import { ResponderComponent } from './responder/responder.component';

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'cadastrar', component: CadastroComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'questoes', component: QuestoesComponent, canActivate: [AuthGuard] },
  { path: 'planos', component: PlanosComponent, canActivate: [AuthGuard] },
  { path: 'pesquisas', component: PesquisasComponent, canActivate: [AuthGuard] },
  { path: 'contatos', component: ContatosComponent, canActivate: [AuthGuard] },
  { path: 'configuracoes', component: ConfiguracoesComponent, canActivate: [AuthGuard] },
  { path: 'relatorios/:id', component: RelatoriosComponent, canActivate: [AuthGuard] },
  { path: 'admin/planos', component: AdminPlanosComponent, canActivate: [AdminGuard] },
  { path: 'responder', component: ResponderComponent }
];
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
from src.globalvars import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from src.models.user_model import User
from src.models.plan_model import Plan
from src.models.contatos_model import Contatos
from src.models.pesquisa_model import Pesquisa

class EmailSender:
    """
    Classe para gerenciar o envio de emails usando SMTP
    
    Attributes:
        smtp_server (str): Servidor SMTP
        smtp_port (int): Porta do servidor SMTP
        smtp_username (str): Usuário do servidor SMTP
        smtp_password (str): Senha do servidor SMTP
    """
    
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Envia um email usando SMTP
        
        Args:
            to_email (str): Email do destinatário
            subject (str): Assunto do email
            body (str): Corpo do email em texto plano
            html_body (str, optional): Corpo do email em HTML
            cc (List[str], optional): Lista de emails em cópia
            bcc (List[str], optional): Lista de emails em cópia oculta
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
            
        Raises:
            Exception: Se houver erro ao enviar o email
        """
        try:
            # Cria a mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Adiciona o corpo em texto plano
            msg.attach(MIMEText(body, 'plain'))
            
            # Adiciona o corpo em HTML se fornecido
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Lista de todos os destinatários
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Conecta ao servidor SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Habilita TLS
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, self.smtp_username, recipients)
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            raise e
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """
        Envia um email de boas-vindas para novos usuários
        
        Args:
            to_email (str): Email do usuário
            user_name (str): Nome do usuário
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
        subject = "Bem-vindo ao ComVoz!"
        
        body = f"""
        Olá {user_name},
        
        Bem-vindo ao ComVoz! Estamos muito felizes em ter você conosco.
        
        Com o ComVoz, você pode:
        - Criar pesquisas personalizadas
        - Gerenciar seus contatos
        - Analisar resultados
        - E muito mais!
        
        Se precisar de ajuda, não hesite em nos contatar.
        
        Atenciosamente,
        Equipe ComVoz
        """
        
        html_body = f"""
        <html>
            <body>
                <h2>Bem-vindo ao ComVoz!</h2>
                <p>Olá {user_name},</p>
                <p>Estamos muito felizes em ter você conosco.</p>
                <h3>Com o ComVoz, você pode:</h3>
                <ul>
                    <li>Criar pesquisas personalizadas</li>
                    <li>Gerenciar seus contatos</li>
                    <li>Analisar resultados</li>
                    <li>E muito mais!</li>
                </ul>
                <p>Se precisar de ajuda, não hesite em nos contatar.</p>
                <p>Atenciosamente,<br>Equipe ComVoz</p>
            </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_plan_interest_notification_without_plan(self, comprador: User, plano: Plan, admin: List[User]) -> bool:
        """
        Envia uma notificação sobre interesse em um plano
        
        Args:
            comprador (User): Usuário que teve interesse
            plano (Plan): Plano que o usuário teve interesse
            admin (User): Administrador que receberá a notificação
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """

        for user_admin in admin:
            subject = f"Interesse no plano {plano.nome} registrado!"
            
            body = f"""
            Olá {user_admin.nome_completo},
            
            O cliente {comprador.nome_completo} com o email {comprador.email} e telefone {comprador.telefone} teve interesse no plano {plano.nome} .
        
            Entre em contato com o cliente para concluir a venda.
        
            Atenciosamente,
            Equipe ComVoz
            """
        
            html_body = f"""
            <html>
            <body>
                <h2>Interesse no plano {plano.nome} registrado!</h2>
                <p>Olá {user_admin.nome_completo},</p>
                <p>O cliente {comprador.nome_completo} com o email {comprador.email} e telefone {comprador.telefone} teve interesse no plano {plano.nome} .</p>
                <p>Entre em contato com o cliente para concluir a venda.</p>
                <p>Atenciosamente,<br>Equipe ComVoz</p>
                </body>
            </html>
            """
        
            self.send_email(user_admin.email, subject, body, html_body) 

        return True
    
    def send_plan_interest_notification_with_plan(self, comprador: User, plano: Plan, admin: List[User], plano_do_usuario: Plan) -> bool:
        """
        Envia uma notificação sobre interesse em um plano
        
        Args:
            comprador (User): Usuário que teve interesse
            plano (Plan): Plano que o usuário teve interesse
            admin (User): Administrador que receberá a notificação
            plano_do_usuario (Plan): Plano que o usuário já possui
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
        
        for user_admin in admin:
            subject = f"Interesse no plano {plano.nome} registrado!"
            
            body = f"""
            Olá {user_admin.nome_completo},
            
            O cliente {comprador.nome_completo} com o email {comprador.email} e telefone {comprador.telefone} teve interesse no plano {plano.nome} .
        
            O cliente já possui o plano {plano_do_usuario.nome} e deseja contratar o plano {plano.nome}. A diferenca para ser paga será {plano.preco - plano_do_usuario.preco} reais e ele terá um acrescimo de {plano.limite_pesquisas - plano_do_usuario.limite_pesquisas} pesquisas e {plano.limite_de_envios - plano_do_usuario.limite_de_envios} de envios de pesquisas.
        
            Entre em contato com o cliente para concluir a venda.
        
            Atenciosamente,
            Equipe ComVoz
            """
            
            html_body = f"""
            <html>
                <body>
                    <h2>Interesse no plano {plano.nome} registrado!</h2>
                    <p>Olá {user_admin.nome_completo},</p>
                    <p>O cliente {comprador.nome_completo} com o email {comprador.email} e telefone {comprador.telefone} teve interesse no plano {plano.nome} .</p>
                    <p>O cliente já possui o plano {plano_do_usuario.nome} e deseja contratar o plano {plano.nome}. A diferenca para ser paga será {plano.preco - plano_do_usuario.preco} reais e ele terá um acrescimo de {plano.limite_pesquisas - plano_do_usuario.limite_pesquisas} pesquisas e  {plano.limite_de_envios - plano_do_usuario.limite_de_envios} de envios de pesquisas.</p>
                    <p>Entre em contato com o cliente para concluir a venda.</p>
                    <p>Atenciosamente,<br>Equipe ComVoz</p>
                </body>
            </html>
            """
            
            self.send_email(user_admin.email, subject, body, html_body)
            
        return True

    def send_pesquisa(self, contatos: List[Contatos], pesquisa: Pesquisa, empresa: str) -> bool:
        """
        Envia uma pesquisa para vários contatos
        """
        for contato in contatos:
            subject = f"Pesquisa de Satisfação - {pesquisa.titulo}"
            
            body = f"""
            Olá {contato.nome},
            
            A empresa {empresa} está realizando uma pesquisa de satisfação (NPS) para entender melhor a experiência de seus clientes.
            
            Sua opinião é muito importante para nós! Por favor, reserve alguns minutos para responder nossa pesquisa:
            
            {pesquisa.descricao}
            
            Para responder a pesquisa, acesse o link abaixo:
            http://localhost:4200/responder?id={pesquisa.id}
            
            Agradecemos sua participação!
            
            Atenciosamente,
            Equipe ComVoz
            """
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <h2 style="color: #2c3e50;">Pesquisa de Satisfação - {pesquisa.titulo}</h2>
                    
                    <p>Olá <strong>{contato.nome}</strong>,</p>
                    
                    <p>A empresa <strong>{empresa}</strong> está realizando uma pesquisa de satisfação (NPS) para entender melhor a experiência de seus clientes.</p>
                    
                    <p>Sua opinião é muito importante para nós! Por favor, reserve alguns minutos para responder nossa pesquisa:</p>
                    
                    <p style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #2c3e50;">
                        {pesquisa.descricao}
                    </p>
                    
                    <p>Para responder a pesquisa, clique no botão abaixo:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:4200/responder?id={pesquisa.id}" 
                           style="background-color: #2c3e50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Responder Pesquisa
                        </a>
                    </div>
                    
                    <p>Ou acesse o link: <a href="http://localhost:4200/responder?id={pesquisa.id}">http://localhost:4200/responder?id={pesquisa.id}</a></p>
                    
                    <p>Agradecemos sua participação!</p>
                    
                    <p style="margin-top: 30px;">
                        Atenciosamente,<br>
                        <strong>Equipe ComVoz</strong>
                    </p>
                </body>
            </html>
            """
            
            self.send_email(contato.email, subject, body, html_body)
            
        return True



from flask_smorest import Blueprint, abort
from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.controllers.dashboard_controller import get_dashboard_principal_data, get_dados_relatorio_pesquisa
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import io
import os
from src.controllers.dashboard_controller import get_estatisticas_pesquisa_frontend


dashboard_blueprint = Blueprint("dashboard", __name__, description="Endpoints para o dashboard")



@dashboard_blueprint.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    try:
        user_id = int(get_jwt_identity())
        
        dashboard_data = get_dashboard_principal_data(user_id)
        
        return jsonify(dashboard_data), 200
        
        
    except Exception as e:
        return jsonify({"error": "Erro ao obter o dashboard"}), 500


@dashboard_blueprint.route("/relatorio/<string:pesquisa_id>", methods=["GET"])
@jwt_required()
def get_relatorio_pesquisa(pesquisa_id):
    try:
        user_id = int(get_jwt_identity())
        
        metrics = get_dados_relatorio_pesquisa(pesquisa_id)
        
        # Criar buffer para o PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)  # Usando orientação retrato
        styles = getSampleStyleSheet()
        elements = []
        
        # Título do relatório
        elements.append(Paragraph(f"Relatório da Pesquisa: {metrics['titulo_pesquisa']}", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Informações gerais
        elements.append(Paragraph("Informações Gerais", styles['Heading2']))
        elements.append(Paragraph(f"Total de Respostas: {metrics['total_respostas']}", styles['Normal']))
        elements.append(Paragraph(f"NPS Geral: {metrics['nps_geral']:.2f}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Gráfico NPS Geral por Questão
        plt.figure(figsize=(10, 6))
        perguntas = [p['texto'][:30] + '...' for p in metrics['perguntas']]
        nps_values = [p['nps']['nps_score'] for p in metrics['perguntas']]
        
        plt.bar(perguntas, nps_values)
        plt.title("NPS Score por Questão", fontsize=14, pad=20)
        plt.xlabel("Questões", fontsize=12)
        plt.ylabel("NPS Score", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Salvar o gráfico principal
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        elements.append(Image(img_buffer, width=500, height=300))
        elements.append(Spacer(1, 12))
        
        # Tabela detalhada na primeira página
        elements.append(Paragraph("Detalhamento por Questão", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Cabeçalho da tabela
        data = [['Questão', 'NPS', 'Total Respostas', 'Detratores', 'Neutros', 'Promotores']]
        
        # Dados da tabela
        for pergunta in metrics['perguntas']:
            data.append([
                pergunta['texto'][:50] + '...',
                f"{pergunta['nps']['nps_score']:.2f}",
                str(pergunta['total_respostas']),
                str(pergunta['distribuicao']['1-6']),
                str(pergunta['distribuicao']['7-8']),
                str(pergunta['distribuicao']['9-10'])
            ])
        
        # Criar e estilizar a tabela
        table = Table(data, colWidths=[250, 60, 80, 60, 60, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ]))
        
        elements.append(table)
        elements.append(PageBreak())  # Quebra de página após a tabela
        
        # Gráficos individuais para cada pergunta (2 por página)
        for i in range(0, len(metrics['perguntas']), 2):
            # Primeiro gráfico da página
            plt.figure(figsize=(8, 5))
            pergunta = metrics['perguntas'][i]
            categorias = ['Detratores', 'Neutros', 'Promotores']
            valores = [
                pergunta['distribuicao']['1-6'],
                pergunta['distribuicao']['7-8'],
                pergunta['distribuicao']['9-10']
            ]
            
            plt.bar(categorias, valores)
            plt.title(f"{pergunta['texto'][:50]}...", fontsize=10, pad=15)
            plt.xlabel("Categorias", fontsize=9)
            plt.ylabel("Número de Respostas", fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Adicionar valores em cima das barras
            for j, v in enumerate(valores):
                plt.text(j, v, str(v), ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Salvar o primeiro gráfico
            img_buffer1 = io.BytesIO()
            plt.savefig(img_buffer1, format='png', dpi=300, bbox_inches='tight')
            img_buffer1.seek(0)
            elements.append(Image(img_buffer1, width=400, height=250))
            
            # Se houver uma segunda pergunta para esta página
            if i + 1 < len(metrics['perguntas']):
                plt.figure(figsize=(8, 5))
                pergunta = metrics['perguntas'][i + 1]
                valores = [
                    pergunta['distribuicao']['1-6'],
                    pergunta['distribuicao']['7-8'],
                    pergunta['distribuicao']['9-10']
                ]
                
                plt.bar(categorias, valores)
                plt.title(f"{pergunta['texto'][:50]}...", fontsize=10, pad=15)
                plt.xlabel("Categorias", fontsize=9)
                plt.ylabel("Número de Respostas", fontsize=9)
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Adicionar valores em cima das barras
                for j, v in enumerate(valores):
                    plt.text(j, v, str(v), ha='center', va='bottom')
                
                plt.tight_layout()
                
                # Salvar o segundo gráfico
                img_buffer2 = io.BytesIO()
                plt.savefig(img_buffer2, format='png', dpi=300, bbox_inches='tight')
                img_buffer2.seek(0)
                elements.append(Image(img_buffer2, width=400, height=250))
            
            # Adicionar quebra de página após cada par de gráficos
            if i + 2 < len(metrics['perguntas']):
                elements.append(PageBreak())
        
        # Construir o PDF
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'relatorio_pesquisa_{pesquisa_id}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar relatório: {str(e)}"}), 500


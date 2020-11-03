import pandas as pd
from datetime import datetime

precos_licitacao={1:(500,1,14.70,   'Alcool em Gel 70% 500ml'),
                  2:(1200,1,118.10, 'Alcool em Gel 70% 5L'),
                  3:(1000,1,62.00,  'Alcool Etílico 70% 5L'),
                  4:(230,12,38.90,   'Desinfetante Líq. 1l 12und'),
                  5:(200,24,36.00,   'Detergente 500ml 24und'),
                  6:(400,1,10.90,   'Toalha de Papel 23x21cm 1000 folhas'),
                  7:(402,1,17.89,   'Saco Lixo 30l 100und'),
                  8:(400,1,20.7,    'Saco de Lixo 50l 100und'),
                  9:(1000,1,47.0,   'Luva de Proced. grand 100und'),
                  10:(1100,1,47.0,  'Luva de Proced.média 100und'),
                  11:(700,1,47.0,   'Luva de Proced. peque 100und'),
                  12:(1500,1,255.0, 'Masc. Cirurg. tripla 50und'),
                  13:(7000,1,28.19, 'Masc. Respirador PFF2'),
                  14:(400,1,11.90,  'Óculos de Protecao'),
                  15:(500,1,24.92,  'Touca descatável 100und'),
                  16:(300,1,42.0,   'Saco Lixo 100l 100und')}


class PrecosLicitacao():

    def __init__(self,arquivo_cotacao='dl.032.2020.xlsx',proposta_vencedora=precos_licitacao):
        self.arquivo_cotacao = arquivo_cotacao
        self.proposta_vencedora = proposta_vencedora
        self.carregar_planilha()

    def obter_proposta_vencedora(self):
        dados = [(chave,value[0],value[1],value[2],value[3]) for chave,value in self.proposta_vencedora.items()]
        colunas = ['item','qt_licitada','qt_por_item','vl_unitario','descricao']
        df = pd.DataFrame(dados,columns=colunas)
        df['vl_total'] = df['qt_licitada'] * df['qt_por_item'] * df['vl_unitario']
        return df[['item','descricao','qt_licitada','qt_por_item','vl_unitario','vl_total']].sort_values(by=['item'])

    def carregar_planilha(self):
        colunas_de_datas = ['data_compra','data_consulta']
        planilha = pd.read_excel(self.arquivo_cotacao,\
                                     parse_dates=colunas_de_datas)
        planilha['qt_licitada'] = planilha.item.apply(self.get_info_licitacao,tipo='quant_licitada')
        planilha['vl_unit_licitado'] = planilha.item.apply(self.get_info_licitacao,tipo='preco_unitario')
        planilha['quant_por_item'] = planilha.item.apply(self.get_info_licitacao,tipo='quant_por_item')
        planilha['desc_item'] = planilha.item.apply(self.get_info_licitacao,tipo='desc_item')
        planilha['variacao_preco'] = planilha.valor_minimo/planilha.valor_medio
        self.planilha_de_precos = planilha
        return planilha

    def diferencas_de_precos(self,lista_gtin,periodicidade,dia_mes):
        if periodicidade  == 'diario':
            filtro_data = self.planilha_de_precos.data_compra == datetime.strptime(dia_mes,'%Y-%m-%d') 
        else:
            filtro_data = self.planilha_de_precos.data_compra.dt.month == dia_mes 

        filtro = ( self.planilha_de_precos.codigo_barras.isin(lista_gtin)) &\
                 ( filtro_data) &\
                 ((self.planilha_de_precos.periodicidade == periodicidade))
        amostra = self.planilha_de_precos[filtro][:]
        amostra['dif_por_item'] = amostra['vl_unit_licitado'] - (amostra['valor_medio'] * amostra['quant_por_item'])
        amostra['dif_total'] = amostra['qt_licitada'] * amostra['dif_por_item']
        colunas = ['item','codigo_barras','produto','data_compra',\
                   'valor_medio','vl_unit_licitado','quant_por_item',\
                   'dif_por_item','qt_licitada','dif_total']
        ordenado_por = ['item','codigo_barras','data_compra']
        return amostra[colunas].sort_values(by=ordenado_por,ascending=True)
    #items_licitados = planilha.groupby([  'item',
    #                                   'desc_item',
    #                                   'qt_licitada',
    #                                   'vl_unit_licitado',
    #                                   'quant_por_item'], as_index=False)['quant_por_item'].first()
    #items_licitados.columns = ['Item', 'Descrição', 'Quant','Vl Unit', 'Quant.p/Item']
    #items_licitados

    def get_info_licitacao(self,index,tipo=''):
        if tipo == 'quant_licitada':
            return self.proposta_vencedora.get(index)[0]
        elif tipo == 'quant_por_item':
            return self.proposta_vencedora.get(index)[1]
        elif tipo == 'preco_unitario':
            return self.proposta_vencedora.get(index)[2]
        elif tipo == 'desc_item':
            return self.proposta_vencedora.get(index)[3]
        else :
            return None

def obter_variacoes_de_precos(data,periodicidade,order_by=True):
    filtro = data.periodicidade == periodicidade
    variacoes_de_preco = data[filtro]
    variacoes_de_preco = variacoes_de_preco.groupby(['produto',
                                                     'codigo_barras',
                                                     'periodicidade'], 
                                                     as_index=False)[['variacao_preco']].max()
    variacoes_de_preco = variacoes_de_preco.sort_values(by=['variacao_preco'], 
                                                        ascending=order_by)
    variacoes_de_preco.columns = ['Produto', 
                                  'Código de Barras', 
                                  'Periodicidade',
                                  'Variação do Preço']
    
    #variacoes_de_preco.head(20)
    return variacoes_de_preco

def estatisticas_preco_medio(dados,periodicidade,order_by):
    filtro = dados.periodicidade == periodicidade
    estatisticas = dados[filtro]
    estatisticas = estatisticas.groupby(['produto',
                                         'codigo_barras',
                                         'periodicidade'], 
                                         as_index=False)[['valor_medio']].aggregate(['max',
                                                                                     'mean',
                                                                                     'min',
                                                                                     'count',
                                                                                     'std'])
    estatisticas.columns = ['Preço Máximo',
                            'Preço Médio',
                            'Preço Mínimo',
                            'Quantidade',
                            'Desvio Padrão']
    estatisticas = estatisticas.sort_values(by=['Desvio Padrão'], ascending=order_by)
    return estatisticas

if __name__ == '__main__':
    
    precos = PrecosLicitacao()
    df = precos.diferencas_de_precos([7897010402008,7897010402084,7897010408260],\
                                'diario','2020-04-28')
    print(df)

#colunas = ['item','produto','codigo_barras','data_compra','valor_medio',
#            'vl_unit_licitado','quant_por_item','dif_por_item',
#            'qt_licitada','dif_total']
#estilo = {'data_compra'      : "{:%d/%m/%Y}",
#          'valor_medio'      : lambda x: f'{locale.format("%.2f", x, True)}',
#          'vl_unit_licitado' : lambda x: f'{locale.format("%.2f", x, True)}',
#          'dif_por_item'     : lambda x: f'{locale.format("%.2f", x, True)}',
#          'dif_total'        : lambda x: f'{locale.format("%.2f", x, True)}'}
#s = amostra[colunas].style.format(estilo) #.style.hide_index()
#s.hide_index()


#produtos_por_item = produtos_por_item.rename(columns={'desc_item':'Item',
#                                                                 'codigo_barras':'Qt Similares'})
    

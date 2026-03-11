STATION_MAP = {
   0:'Novo Eldorado', 1: 'Eldorado', 2: 'Cidade Industrial', 3: 'Vila Oeste', 4: 'Gameleira', 
    5: 'Calafate', 6: 'Carlos Prates', 7: 'Lagoinha', 8: 'Central', 
    9: 'Santa Efigênia', 10: 'Santa Tereza', 11: 'Horto', 12: 'Santa Inês', 
    13: 'José Cândido', 14: 'Minas Shopping', 15: 'São Gabriel', 
    16: 'Primeiro de Maio', 17: 'Waldomiro Lobo', 18: 'Floramar', 19: 'Vilarinho'
}

STATION_NAME_TO_ID = {v: k for k, v in STATION_MAP.items()}

ALL_TABS = [
    "carga_csv", 
    "configuracoes",
    "documentacao",
    "ia_ml",
    "sql_scripts", 
    "operacao", 
    "indicadores", 
    "numeros",
    "ia_avancada"
]

TABLES_CONFIG = {
    'tab01': ['mesref', 'tipo_dia', 'fx_hora', 'viagens', 'tempo_percurso', 'disp_frota'],
    'tab02': ['data_completa', 'hora_completa', 'entrada_id', 'cod_estacao', 'bloqueio_id','dbd_num', 'grupo_bilhete', 'forma_pagamento', 'tipo_bilhete', 'user_id', 'valor'],
    'tab02_temp2': ['data_hora_corrigida', 'estacao', 'bloqueio', 'grupo_bilhete', 'forma_pagamento','tipo_de_bilhete'],
    'tab02_marco': ['entrada_id', 'hora_completa', 'cod_estacao', 'bloqueio_id', 'dbd_num', 'grupo_bilhete','forma_pagamento', 'tipo_bilhete', 'user_id', 'data_completa', 'valor'],
    'tab03_old': ['ordem', 'dia', 'viagem', 'origemprevista', 'origemreal', 'destinoprevisto', 'destinoreal','horainicioreal', 'horainicioprevista', 'horafimprevista', 'horafimreal', 'trem', 'status','stat_desc', 'picovale', 'incidenteleve', 'incidentegrave', 'viagem_interrompida', 'id_ocorr','id_interrupcao', 'id_linha', 'lotacao'],
    'tab03': ['id','ordem', 'dia', 'viagem', 'origemreal', 'destinoreal', 'horainicioreal', 'horafimreal', 'trem', 'status', 'incidenteleve', 'incidentegrave','stat_desc',  'id_ocorr', 'id_interrupcao', 'id_linha', 'horainicioprevista', 'horafimprevista',  'lotacao'],
    'arq3_dadosviagens': ['ordem', 'dia', 'viagem', 'origem', 'destino', 'hora_inicio', 'hora_fim', 'veiculo','tipo_real', 'incidente_leve', 'incidente_grave', 'viagem_interrompida'],
    'tab04': ['id', 'tipo', 'subtipo', 'data', 'horaini', 'horafim', 'motivo', 'local', 'env_usuario','env_veiculo', 'bo'],
    'tab05': ['nome_linha', 'status_linha', 'fim_operacao', 'cod_estacao', 'grupo_bilhete', 'ini_operacao','num_estacao', 'max_valor'],
    'tab06': ['ordem', 'emissao', 'data', 'hora', 'tipo', 'trem', 'cdv', 'estacao', 'via', 'viagem', 'causa','excluir', 'motivo_da_exclusao'],
    'tab07': ['linha', 'cod_estacao', 'estacao', 'bloqueio', 'c_empresa_validador', 'dbd_num', 'dbd_data','valid_ex_emp', 'valid_ex_num', 'valid_ex_data'],
    'tab08': ['equipamento', 'descricao', 'modelo', 'serie', 'data_inicio_operacao', 'data_fim_operacao'],
    'tab09': ['tue', 'data', 'hora_inicio', 'hora_fim', 'origem', 'destino', 'descricao', 'status', 'km'],
    'tab14': ['composicao', 'data_abertura', 'data_fechamento', 'tipo_manutencao', 'tipo_desc', 'tipo_falha'],
    'arq15_tueoperacoes': ['tue', 'data', 'hora_inicio', 'hora_fim', 'origem', 'destino', 'descricao'],
    'tab12': ['referencia', 'num_instalacao', 'tipo', 'total_kwh', 'local', 'endereco'],
    'tab13': ['cdv', 'sent_normal_circ', 'comprimento', 'cod_velo_max', 'plat_est', 'temp_teor_perc','temp_med_perc', 'tempoocup'],
    'arq1_resumoviagensfrota ': ['mesref', 'dia', 'hora', 'viagens', 'tempo_percurso', 'disp_frota'],
    'arq02_bilhetagem': ['entrada_id', 'hora_completa', 'cod_estacao', 'bloqueio', 'dbd_num','grupo_bilhetagem', 'forma_pagamento', 'tipo_de_bilhete', 'user_id', 'data_completa', 'valor'],
    'arq04_ocorrencias': ['id', 'tipo', 'subtipo', 'data', 'horaini', 'horafim', 'motivo', 'local','env_usuario', 'env_veiculo', 'bo'],
    'arq4_1_reclamacoesusuarios': ['tipo', 'dt', 'motivo'],
    'arq4_2_manutencao': ['tipo', 'data', 'subtipo', 'hora', 'local'],
    'arq4_3_seguranca': ['tipo', 'data', 'hora_inicio', 'hora_fim', 'local'],
    'arq5_1_falhasmanutencao': ['data_abertura', 'composicao', 'data_fechamento', 'tipo_manutencao', 'tipo_de_falha'],
    'arq05_8_nece_disp': ['ordem', 'data', 'hora', 'necessidade', 'disponibilidade'],
    'arq07_linhas': ['num_estacao', 'nome_linha', 'ini_operacao', 'status_linha', 'fim_operacao', 'cod_estacao','max_valor', 'grupo_bilhete'],
    'arq07_paradas': ['num_estacao', 'estacao', 'cod_estacao', 'sistemas_que_operam'],
    'arq8_statusviagens ': ['ordem', 'dia', 'viagem', 'origem_prevista', 'origem_real', 'destino_previsto','destino_real', 'hora_inicio_prevista', 'hora_inicio_real', 'hora_fim_prevista','hora_fim_real', 'trem', 'status', 'pico_vale'],
    'arq9_validacaobilhetes ': ['estacao', 'dbd_id', 'data_hora_corrigida', 'forma_pagamento', 'tipo_de_bilhete'],
    'arq08_03_11_15_viagens': ['ordem', 'dia', 'viagem', 'origem_previa', 'origem_real', 'destino_previo','destino_real', 'hora_ini_prevista', 'hora_ini_real', 'hora_fim_prevista','hora_fim_real', 'trem', 'status', 'desc_status', 'pico_vale', 'incidente_leve','incidente_grave', 'viagem_interrompida', 'id_ocorrencia', 'id_interrupcao','id_linha', 'lotacao'],
    'arq11_detalhesviagens': ['data', 'id_viagem', 'hora_inicio_programada', 'hora_fim_programada','hora_inicio_realizada', 'status', 'interrupcao', 'lotacao_maxima', 'tpppm', 'tprpm','tpppt', 'tprpt', 'tppfp', 'tprfp'],
    'arq12': ['ordem', '"emissao"', 'data', 'hora', 'tipo', 'trem', 'cdv', 'estacao', 'via', 'viagem', 'causa','excluir', 'motivo'],
    'arq16_bloqueios': ['cod_estacao', 'estacao', 'bloqueio', 'dbd_id', 'data_pass', 'qtd_passageiros','max_num_est', 'min_bloqueio'],
    'tab_06_validadores': ['linha', 'cod_est', 'estacao', 'bloqueio', 'dbd_emp', 'dbd_num', 'dbd_data','valid_ext_emp', 'valida_ext_data'],
    'tab_13_cdv': ['cdv', 'sentido_circulacao', 'comprimento', 'cod_vel_max', 'plataforma_estacao','tempo_teorico_perc', 'tempo_medido_perc', 'tempo_ocupacao'],
    'tab_consumo_energia': ['referencia', 'num_instalacao', 'tipo', 'total_kwh', 'local', 'endereco'],
}

# (Por questão de tamanho, cole aqui a sua lista inteira de INSERTS_PREDEFINIDOS original)
INSERTS_PREDEFINIDOS = [
    {
        'nome': "Padronização de Nomes",
        'sql': """
            update migracao.tab01 set tipo_dia = 'Domingos e Feriados' where tipo_dia = 'domingo e feriado';
            update migracao.tab01 set tipo_dia = 'Sabados' where tipo_dia = 'sabado';
            update migracao.tab01 set tipo_dia = 'Dias Uteis' where tipo_dia = 'Dia util' or tipo_dia = 'Dia Util' or tipo_dia = 'dia util' or tipo_dia = 'util';
            update migracao.tab01 set mesref = replace (mesref,'/','-');
            update migracao.tab01 set viagens  = replace (viagens,'.0','');
            update migracao.tab02 set dbd_num = id from public.validador i where dbd_num = i.dbd_id;
            update migracao.tab02_marco set dbd_num = id from public.validador i where dbd_num = i.dbd_id;
            update migracao.tab01 set tempo_percurso  = '00:00:00' where tempo_percurso ='nan' ;
            update migracao.tab01 set disp_frota  = '0' where disp_frota  ='nan';
            update migracao.tab09 set tue = t.id from public.frota t where tue = t.cod_trem ;
            update migracao.tab09 set tue = t.id from public.frota t where tue = t.cod_trem ;
            update migracao.tab14 a set composicao = t.id from public.frota t where a.composicao = t.cod_trem;   
            update migracao.tab02 set cod_estacao = 1 where cod_estacao ='ELD';
            update migracao.tab02 set cod_estacao = 2 where cod_estacao = 'CID'; 
            update migracao.tab02 set cod_estacao = 3 where cod_estacao = 'VOS';
            update migracao.tab02 set cod_estacao = 4 where cod_estacao = 'GAM';
            update migracao.tab02 set cod_estacao = 5 where cod_estacao = 'CAL';
            update migracao.tab02 set cod_estacao = 6 where cod_estacao = 'CAP';
            update migracao.tab02 set cod_estacao = 7 where cod_estacao ='LAG';
            update migracao.tab02 set cod_estacao = 8 where cod_estacao = 'CNT';
            update migracao.tab02 set cod_estacao = 9 where cod_estacao = 'SAE';
            update migracao.tab02 set cod_estacao = 10 where cod_estacao = 'SAT';
            update migracao.tab02 set cod_estacao = 11 where cod_estacao = 'HOT';
            update migracao.tab02 set cod_estacao = 12 where cod_estacao = 'SAI';
            update migracao.tab02 set cod_estacao = 13 where cod_estacao = 'JCS';
            update migracao.tab02 set cod_estacao = 14 where cod_estacao = 'MSH';
            update migracao.tab02 set cod_estacao = 15 where cod_estacao = 'SGB';
            update migracao.tab02 set cod_estacao = 16 where cod_estacao = 'PRM';
            update migracao.tab02 set cod_estacao = 17 where cod_estacao = 'WLB';
            update migracao.tab02 set cod_estacao = 18 where cod_estacao = 'FLO';
            update migracao.tab02 set cod_estacao = 19 where cod_estacao = 'VRO';
            update migracao.tab02 set valor  = '5.50'  where valor = '5,5';
            update migracao.tab02_marco set cod_estacao = 1 where cod_estacao ='ELD';
            update migracao.tab02_marco set cod_estacao = 2 where cod_estacao = 'CID';  
            update migracao.tab02_marco set cod_estacao = 3 where cod_estacao = 'VOS';
            update migracao.tab02_marco set cod_estacao = 4 where cod_estacao = 'GAM';
            update migracao.tab02_marco set cod_estacao = 5 where cod_estacao = 'CAL';
            update migracao.tab02_marco set cod_estacao = 6 where cod_estacao = 'CAP';
            update migracao.tab02_marco set cod_estacao = 7 where cod_estacao ='LAG';
            update migracao.tab02_marco set cod_estacao = 8 where cod_estacao = 'CNT';
            update migracao.tab02_marco set cod_estacao = 9 where cod_estacao = 'SAE';
            update migracao.tab02_marco set cod_estacao = 10 where cod_estacao = 'SAT';
            update migracao.tab02_marco set cod_estacao = 11 where cod_estacao = 'HOT';
            update migracao.tab02_marco set cod_estacao = 12 where cod_estacao = 'SAI';
            update migracao.tab02_marco set cod_estacao = 13 where cod_estacao = 'JCS';
            update migracao.tab02_marco set cod_estacao = 14 where cod_estacao = 'MSH';
            update migracao.tab02_marco set cod_estacao = 15 where cod_estacao = 'SGB';
            update migracao.tab02_marco set cod_estacao = 16 where cod_estacao = 'PRM';
            update migracao.tab02_marco set cod_estacao = 17 where cod_estacao = 'WLB';
            update migracao.tab02_marco set cod_estacao = 18 where cod_estacao = 'FLO';
            update migracao.tab02_marco set cod_estacao = 19 where cod_estacao = 'VRO';
            update migracao.tab02_marco set valor  = '5.50'  where valor = '5,5';
            update migracao.tab07  set cod_estacao = 1 where cod_estacao ='ELD';
            update migracao.tab07 set cod_estacao = 2 where cod_estacao = 'CID';    
            update migracao.tab07 set cod_estacao = 3 where cod_estacao = 'VOS';
            update migracao.tab07 set cod_estacao = 4 where cod_estacao = 'GAM';
            update migracao.tab07 set cod_estacao = 5 where cod_estacao = 'CAL';
            update migracao.tab07 set cod_estacao = 6 where cod_estacao = 'CAP';
            update migracao.tab07 set cod_estacao = 7 where cod_estacao = 'LAG';
            update migracao.tab07 set cod_estacao = 8 where cod_estacao = 'CNT';
            update migracao.tab07 set cod_estacao = 9 where cod_estacao = 'SAE';
            update migracao.tab07 set cod_estacao = 10 where cod_estacao = 'SAT';
            update migracao.tab07 set cod_estacao = 11 where cod_estacao = 'HOT';
            update migracao.tab07 set cod_estacao = 12 where cod_estacao = 'SAI';
            update migracao.tab07 set cod_estacao = 13 where cod_estacao = 'JCS';
            update migracao.tab07 set cod_estacao = 14 where cod_estacao = 'MSH';
            update migracao.tab07 set cod_estacao = 15 where cod_estacao = 'SGB';
            update migracao.tab07 set cod_estacao = 16 where cod_estacao = 'PRM';
            update migracao.tab07 set cod_estacao = 17 where cod_estacao = 'WLB';
            update migracao.tab07 set cod_estacao = 18 where cod_estacao = 'FLO';
            update migracao.tab07 set cod_estacao = 19 where cod_estacao = 'VRO';
            update migracao.tab14 set composicao = replace(composicao, 'TUE ','T');
            update migracao.tab14 T set composicao = ID from public.frota where T.composicao = COD_TREM;
            update migracao.tab03 set trem = i.id from public.frota i where trem = i.cod_trem;
            update migracao.arq8_statusviagens  set trem  = i.id from public.frota i where trem = i.cod_trem;
            update migracao.arq3_dadosviagens  set veiculo  = i.id from public.frota i where veiculo = i.cod_trem;
            delete from migracao.tab03 where status = '12';
            update migracao.tab09 set tue = t.id from public.frota t where tue = t.cod_trem ;
            update migracao.tab09 set hora_inicio = '00:00' where hora_inicio = '';
            update migracao.tab09 set hora_inicio = '00:00' where hora_inicio = ':';
            update migracao.tab09 set hora_fim  = '00:00' where hora_fim = ':';
            update migracao.tab09 set hora_fim  = '00:00' where hora_fim = '';
            update migracao.tab06 t set trem = f.id::varchar from public.frota f where f.cod_trem = t.trem ;
            delete from migracao.tab01 where mesref is null and tipo_dia is null and fx_hora is null   ;      
            update migracao.tab01 set viagens = 0 where viagens is null; 
            update migracao.tab01 set tempo_percurso  = '00:00:00' where tempo_percurso  is null; 
        """,
    },
    {
        'nome': "Validadores",
        'sql': """
            INSERT INTO public.mov_dbd
            (linha, cod_estacao, estacao, bloqueio, c_empresa_validador, dbd_num, dbd_data, valid_ex_emp, valid_ex_num, valid_ex_data)
            SELECT t1.linha::int, t1.cod_estacao::int, t1.estacao, t1.bloqueio::int, t1.c_empresa_validador, t1.dbd_num, TO_CHAR(TO_DATE(t1.dbd_data, 'DD/MM/YYYY'), 'YYYY-MM-DD')::date,
            t1.valid_ex_emp, t1.valid_ex_num::int, TO_CHAR(TO_DATE(t1.valid_ex_data, 'DD/MM/YYYY'), 'YYYY-MM-DD')::date
            FROM migracao.tab07 AS t1
            WHERE NOT EXISTS (
                SELECT 1 FROM public.mov_dbd AS t2
                WHERE t2.linha = t1.linha::int AND t2.cod_estacao = t1.cod_estacao::int AND t2.dbd_num = t1.dbd_num
            );
            INSERT INTO public.validador (dbd_id, bloqueio, validador, tipo)
            SELECT DISTINCT dbd_num, bloqueio_id::INT, 'SEM_DADO', 'MOVIMENTACAO' 
            FROM migracao.tab02
            ON CONFLICT (dbd_id) DO NOTHING;

            update migracao.tab02 v set dbd_num = m.id  from public.validador m where v.dbd_num = m.dbd_id;
            update migracao.tab02_marco  v set dbd_num = m.id  from public.validador m where v.dbd_num = m.dbd_id;
        """,
    },
    {
        'nome': "Quadro de Viagens",
        'sql': """
            INSERT INTO public.ARQ1_PROGPLAN(MESREF, TIPO_DIA, FX_HORA, VIAGENS, TEMPO_PRECURSO, DISP_FROTA)
            SELECT (MESREF || '-01')::date, TIPO_DIA, FX_HORA::TIME, VIAGENS::INT, TEMPO_PERCURSO::TIME, DISP_FROTA::INT
            FROM migracao.tab01 AR;
            
            update public.arq1_progplan set tipo_dia ='Dias Uteis' where tipo_dia = 'Dia Uteis';  
            update public.arq1_progplan set intervalo = '00:07:00' where viagens  = 8;
            update public.arq1_progplan set intervalo = '00:03:30' where viagens  = 16;
            update public.arq1_progplan set intervalo = '00:03:30' where viagens  = 18;
            update public.arq1_progplan set intervalo = '00:03:30' where viagens  = 17;
            update public.arq1_progplan set intervalo = '00:04:00' where viagens  = 15;
            update public.arq1_progplan set intervalo = '00:09:00' where viagens  = 7;
            update public.arq1_progplan set intervalo = '00:30:00' where viagens  = 2;
            update public.arq1_progplan set intervalo = '00:15:00' where viagens  = 4;
            update public.arq1_progplan set intervalo = '00:06:00' where viagens  = 10;
            update public.arq1_progplan set intervalo = '00:03:00' where viagens  = 19;
            update public.arq1_progplan set intervalo = '00:06:30' where viagens  = 9;
            update public.arq1_progplan set intervalo = '00:04:20' where viagens  = 14;
            update public.arq1_progplan set intervalo = '00:04:40' where viagens  = 13;
            update public.arq1_progplan set intervalo = '01:00:00' where viagens  = 0;
            update public.arq1_progplan set intervalo = '00:20:00' where viagens  = 3;
            update public.arq1_progplan set intervalo = '00:05:30' where viagens  = 11;
            update public.arq1_progplan set intervalo = '00:10:00' where viagens  = 6;
            update public.arq1_progplan set intervalo = '00:20:00' where viagens  = 3;
            update public.arq1_progplan set intervalo = '00:05:30' where viagens  = 11;
            update public.arq1_progplan set intervalo = '00:05:00' where viagens  = 12;
            update public.arq1_progplan set intervalo = '00:03:00' where viagens  = 20;
            update public.arq1_progplan set intervalo = '00:12:00' where viagens  = 5;
            update public.arq1_progplan set intervalo = '01:00:00' where viagens  = 1;
            update public.arq1_progplan set intervalo = '00:00:00', tempo_precurso = '00:00:00' where viagens  = 0;
            update public.arq1_progplan set viagens = 0 where viagens is null;
        """,
    },
    {
        'nome': "Bilhetagem",
        'sql': """
            insert into public.arq2_bilhetagem (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM,id_validador,VALOR,USUARIO)
            select CONCAT(ab.data_completa, ' ', ab.hora_completa)::timestamp, ab.cod_estacao ::INT,ab.bloqueio_id::INT,ab.grupo_bilhete ,ab.forma_pagamento ,ab.tipo_bilhete,null,ab.valor ::numeric(3,2),ab.user_id 
            from migracao.tab02 ab 
            ON CONFLICT (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM) DO NOTHING;
            
            insert into public.arq2_bilhetagem (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM,id_validador,VALOR,USUARIO)
            select CONCAT(ab.data_completa, ' ', ab.hora_completa)::timestamp,ab.cod_estacao ::INT,ab.bloqueio_id::INT,ab.grupo_bilhete ,ab.forma_pagamento ,ab.tipo_bilhete,null,ab.valor ::numeric(3,2),ab.user_id 
            from migracao.tab02_marco ab 
            ON CONFLICT (DATA_HORA,ID_ESTACAO,ID_BLOQUEIO,GRUPO_BILHETAGEM,FORMA_PGTO,TIPO_BILHETAGEM) DO NOTHING;                             
        """,
    },
    {
        'nome': "Viagens",
        'sql': """
            insert into public.arq3_viagens (ordem, "data",viagem ,origem, destino, hora_ini, hora_fim,tipo_real,id_veiculo,incidente_leve,incidente_grave,viagem_interrompida,id_ocorrencia, id_interrupcao,id_linha,hora_ini_plan,hora_fim_plan,lotacao,tempo_prog,tempo_real,mtrp,dia_semana,atraso,intervalo)
            select s.ordem::int ,s.dia::date,s.viagem::int,s.origem_prevista,s.destino_real , s.hora_inicio_real::time, s.hora_fim_real::time ,d.tipo_real::int , s.trem::int, case when d.incidente_leve = 'SIM' then true else false end as incleve , case when d.incidente_grave = 'SIM' then true else false end as incgrave , d.viagem_interrompida, null, null, 1, s.hora_inicio_prevista::time , s.hora_fim_prevista::time , null, null, null,null,null,null,null 
            from  migracao.arq8_statusviagens s inner join migracao.arq3_dadosviagens d on s.viagem = d.viagem  and s.dia = d.dia and s.trem = d.veiculo
            ON CONFLICT (ordem,data,viagem,origem,destino,hora_ini,hora_fim) DO NOTHING;      
            insert into public.arq3_viagens (ordem,"data",viagem,origem,destino,hora_ini,hora_fim,tipo_real,id_veiculo,incidente_leve,incidente_grave,viagem_interrompida,id_ocorrencia,id_interrupcao,id_linha,hora_ini_plan,hora_fim_plan )      
            select ordem::int,dia::date,   viagem::int,   origemreal ,   destinoreal ,  horainicioreal::time  ,    horafimreal::time ,    status::int,   trem::int, case when incidenteleve = '' then false    when incidenteleve is null then false  when incidenteleve = 'nao' then false else true    end as inc_leve,   case when incidentegrave = '' then false when incidentegrave is null then false when incidentegrave = 'nao' then false else true  end as inc_grave,  stat_desc ,    id_ocorr::int, id_interrupcao::int,   id_linha::int, t.horainicioprevista::time,    t.horafimprevista::time from migracao.tab03 t
            ON CONFLICT (ordem,data,viagem,origem,destino,hora_ini,hora_fim) DO NOTHING;
            update public.arq3_viagens set viagem_interrompida = 'Sem Interrupcao' where viagem_interrompida = 'Executada';
            update public.arq3_viagens set viagem_interrompida = 'Cancelada Totalmente' where viagem_interrompida = 'Cancelada';
            update public.arq3_viagens set viagem_interrompida = 'Cancelada Parcial' where viagem_interrompida = 'Interrompida';
            delete from public.arq3_viagens where viagem_interrompida in ('Injecao','Recolhimento');
            update public.arq3_viagens set tempo_prog = hora_fim_plan - hora_ini_plan;
            update public.arq3_viagens set tempo_real = hora_fim - hora_ini;
            update public.arq3_viagens set dia_semana = c.dia_semana from public.calendario c where "data" = c.data_calendario;
            update public.arq3_viagens set mtrp = EXTRACT(EPOCH FROM  tempo_real ) /  nullif(EXTRACT(EPOCH FROM  tempo_prog ),0);
            update public.arq3_viagens set dia_semana = 99 where "data" in (select  f.data_feriado from public.feriados f);
            update public.arq3_viagens v set intervalo = p.intervalo  from public.arq1_progplan p where v.dia_semana in (1,2,3,4,5) and extract(hour  from  p.fx_hora) = extract (hour from v.hora_ini) and extract(month from p.mesref) = extract(month from  v."data") and extract(year from v."data") = extract(year from p.mesref) and p.tipo_dia = 'Dias Uteis';
            update public.arq3_viagens v set intervalo = p.intervalo  from public.arq1_progplan p where v.dia_semana in (0,99) and extract(hour  from  p.fx_hora) = extract (hour from v.hora_ini) and extract(month from p.mesref) = extract(month from  v."data") and extract(year from v."data") = extract(year from p.mesref) and p.tipo_dia = 'Domingos e Feriados';
            update public.arq3_viagens v set intervalo = p.intervalo  from public.arq1_progplan p where v.dia_semana in (6) and extract(hour  from  p.fx_hora) = extract (hour from v.hora_ini) and extract(month from p.mesref) = extract(month from  v."data") and extract(year from v."data") = extract(year from p.mesref) and p.tipo_dia = 'Sabados';
            update public.arq3_viagens av set atraso = 0.5 where (av.tempo_prog - av.tempo_real) >= intervalo * 2 and (av.tempo_prog - av.tempo_real) <= intervalo * 3;
            update public.arq3_viagens av set atraso = 0.0 where (av.tempo_prog - av.tempo_real) < intervalo * 2;
            update public.arq3_viagens av set atraso = 0.0 where av.tempo_prog > av.tempo_real;
            update public.arq3_viagens av set atraso = 0.5 where (av.tempo_prog - av.tempo_real) > intervalo * 2 and (av.tempo_prog - av.tempo_real) <= intervalo * 3;
            update public.arq3_viagens av set atraso = 1.0 where (av.tempo_prog - av.tempo_real) > intervalo * 3;
            update public.arq3_viagens  set atraso = 2.0 where incidente_leve is true;
            update public.arq3_viagens set atraso = 4.0 where incidente_grave is true;
        """,
    },
    {
        'nome': "Interrupções de Viagem",
        'sql': """
            INSERT INTO ARQ12_INTERRUPCOES (ID_VIAGEM, ID_OCORRENCIA, ID_VEICULO, TIPO_INCIDENTE, ORIGEM_FALHA, TEMPO_INTERRUPCAO, AMEACAS, DATA_HORA, ID_LOCAL, REFERENCIA, VIA, DESCRICAO, ABONO, JUSTIFICATIVA)
            sELECT a.viagem::int, 0, a.trem::int, 'INTERRUPCAO', a.estacao , a.hora::interval , false , (a."data"  || ' ' || a.hora  )::timestamp  , 0 , a.tipo::varchar(30), a.via, a.causa::varchar(30),false, a.motivo_da_exclusao ::varchar(30)  
            from migracao.tab06 a 
        """,
    },
    {
        'nome': "Ocorrências",
        'sql': """
            insert into public.arq4_ocorrencias (tipo,subtipo,"data",hora_ini,hora_fim,motivo,"local",bo,id_veiculo,id_dispositivo)
            select tipo::varchar(20),subtipo::varchar(20),TO_DATE("data", 'DD/MM/YYYY')::date,horaini::time,horafim::time,motivo,"local",bo,null,null from migracao.tab04 ON CONFLICT (tipo,subtipo,"data",hora_ini,hora_fim,motivo,"local") DO NOTHING;
            
            insert into public.arq4_ocorrencias (tipo,subtipo , "data", motivo, hora_ini,hora_fim)
            select tipo,'RECLAMAÇÃO', dt::date, motivo ,'08:00:00','08:00:00' from migracao.arq4_1_reclamacoesusuarios ao
            ON CONFLICT (tipo,subtipo,"data",hora_ini,hora_fim,motivo,"local") DO NOTHING;
        """,
    },
    {
        'nome': "Manutenção",
        'sql': """
            INSERT INTO public.registros_manutencao (falha, id_tue, data_abertura, data_fechamento, hora_inicio, hora_fim, origem, destino, km, "local", tipo_manutencao ) 
            select distinct  mn.tipo_falha,    op.tue::int,    op."data"::date,    data_fechamento::date ,    op.hora_inicio::time,    op.hora_fim::time,      op.origem ,
            op.destino , op.km,op.status, mn.tipo_desc 
            FROM   migracao.tab09 AS op inner  JOIN    migracao.tab14 AS mn ON    op.tue = mn.composicao AND
            TO_DATE(op."data" , 'DD/MM/YYYY') = TO_DATE(mn.data_abertura, 'DD/MM/YYYY') and OP.status IN( 'MANUT')   group by mn.tipo_falha,
            op.tue,    op."data",    op.hora_inicio,    op.hora_fim ,    mn.data_fechamento,    op.origem ,    op.destino ,    op.km,    op.status,    mn.tipo_desc;
            
            update public.registros_manutencao set tempo_indisponivel = hora_fim - hora_inicio;
        """,
    },
    {
        'nome': "Energia",
        'sql': """
            insert into public.energia (mes_ref, tipo,consumo ,"local" ,num_instalacao  )
            select (referencia || '/01')::date, tipo , total_kwh::numeric,"local" , num_instalacao::numeric  from migracao.tab12
            ON CONFLICT (mes_ref,tipo,consumo,local,num_instalacao) DO NOTHING;
        """,
    },
    {
        'nome': "Disponibilidade Frota",
        'sql': """
            insert into public.disponibilidade_tue (id_tue, "data", hora_inicio,hora_fim,destino,descricao,status,km)
            select tue::INT, "data"::date, hora_inicio::time,hora_fim::time,destino,descricao,status,kM::int from migracao.tab09 where status != 'MANUT';
            
            update public.disponibilidade_tue set horas_disp = hora_fim - hora_inicio;
            
            insert into public.horas_disponiveis (id_tue, mes,horas_disponiveis,horas_operacao)
            with operacao as (
                select sum(horas_disp) horas_ope, id_tue, date_trunc('month',"data")::date mes   
                from public.disponibilidade_tue dt where status = 'OPE' group by id_tue, mes
            ), disponibilidade as (
                select sum(horas_disp) horas_disp, id_tue, date_trunc('month',"data")::date mes  
                from public.disponibilidade_tue dt where status = 'DISP' group by id_tue, mes 
            )
            select o.id_tue, o.mes, d.horas_disp, o.horas_ope  
            from operacao o 
            inner join disponibilidade d on o.id_tue = d.id_tue and o.mes = d.mes
            ON CONFLICT (id_tue, mes, horas_disponiveis) DO NOTHING;
        """,
    },
    {
        'nome': "KM_Percorrida",
        'sql': """
            insert into public.km_percorrida(id_tue, km_inicial, km_final,km_percorrida, mes)
            select tue::int , min (km) as km_inicial, max(km) as km_final,  max (km)- min(km)   as km_percorrido, min("data")::date as "mes" 
            from migracao.tab09 where  status != 'MANUT' group by tue order by tue
            ON CONFLICT (id_tue,km_inicial,km_final,mes) DO NOTHING;
            
            update public.km_percorrida set mes = DATE_TRUNC('month', mes)::date;
        """,
    },
    {
        'nome': "Indisponibilidade - TUE",
        'sql': """
            insert into public.indisponibilidade_tue(id_tue,horas_indisp,mes)
            select distinct id_tue, sum(tempo_indisponivel), DATE_TRUNC('month',data_abertura)::date as data_manut  
            from public.registros_manutencao group by id_tue, data_manut
            ON CONFLICT (id_tue,mes,tipo_manut,horas_indisp) DO NOTHING;
        """,
    },
    {
        'nome': "Frota Status",
        'sql': """
            insert into public.frota_status (id_trem, mes_ref, prod_km,horas_disponivel, horas_operacao, horas_manutencao)
            select hd.id_tue, hd.mes, kp.km_percorrida  , hd.horas_disponiveis, hd.horas_operacao, it.horas_indisp  
            from public.horas_disponiveis hd  
            inner join public.indisponibilidade_tue it on hd.id_tue = it.id_tue and hd.mes = it.mes 
            inner join public.km_percorrida kp on it.id_tue = kp.id_tue and it.mes = kp.mes
            ON CONFLICT (id_trem,mes_ref,prod_km,horas_operacao,horas_disponivel,horas_manutencao) DO NOTHING;
            
            with falhas as (
                select count(*) qtd, DATE_TRUNC('month', rm.data_abertura)::date AS  MES,  id_tue 
                from registros_manutencao rm where tipo_manutencao like 'CORRETIVA' group by id_tue, mes
            )
            update frota_status fr set falhas = f.qtd from falhas f where fr.id_trem = f.id_tue and fr.mes_ref = f.mes;
            update frota_status set falhas = 0 where falhas is null;
        """,
    },
    {
        'nome': "Deletar tabelas de migração",
        'sql': """  
            delete from migracao.tab01;
            delete from migracao.tab02_temp2;
            delete from migracao.tab02_MARCO;
            delete from migracao.tab02;
            delete from migracao.tab03;
            delete from migracao.tab04;
            delete from migracao.tab05;
            delete from migracao.tab06;
            delete from migracao.tab07;
            delete from migracao.tab08;
            delete from migracao.tab09;
            delete from migracao.tab14;
            delete from migracao.tab12;
            delete from migracao.tab13;
            delete from migracao.arq11_detalhesviagens;
            delete from migracao.arq12_excecoesviagens;
            delete from migracao.arq13_1_incidentes;
            delete from migracao.arq13_2_ocorrenciasseguranca;
            delete from migracao.arq15_tueoperacoes;
            delete from migracao.arq16_contagempassageiros;
            delete from migracao.arq17_bloqueios;
            delete from migracao.arq18_equipamentos;
            delete from migracao.arq1_resumoviagensfrota;
            delete from migracao.arq2_dadosbilhetagem;
            delete from migracao.arq3_dadosviagens;
            delete from migracao.arq4_1_reclamacoesusuarios;
            delete from migracao.arq4_2_manutencao;
            delete from migracao.arq4_3_seguranca;
            delete from migracao.arq5_1_falhasmanutencao;
            delete from migracao.arq5_6_dadosfrota;
            delete from migracao.arq5_8_necessidadedisponibilidade;
            delete from migracao.arq7_estacoes;
            delete from migracao.arq8_statusviagens;
            delete from migracao.arq9_validacaobilhetes;
            REFRESH MATERIALIZED VIEW public.vw_resumo_bilhetagem;
            REFRESH MATERIALIZED VIEW public.vw_resumo_viagens;
            REFRESH MATERIALIZED VIEW public.vw_resumo_manutencao;
            REFRESH MATERIALIZED VIEW public.vw_resumo_ocorrencias;
            REFRESH MATERIALIZED VIEW public.vw_resumo_frota;
            REFRESH MATERIALIZED VIEW public.vw_headway_diario_hora;
            REFRESH MATERIALIZED VIEW public.vw_resumo_km_percorrida;
            REFRESH MATERIALIZED VIEW public.vw_headway_mes_hora;
        """,
    }
]
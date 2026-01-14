# /setup - Iniciar Contexto do Projeto

Inicia a coleta de contexto da empresa com o /helper.

## Uso

```
/setup <site ou nome da empresa>
```

## Exemplos

```
/setup www.sympla.com.br
/setup "Nubank"
/setup minha-startup.com
```

## O que acontece

1. /helper pesquisa automaticamente informações públicas
2. Apresenta o que encontrou
3. Faz perguntas sobre o que não é público
4. Cria `.context/empresa.md`
5. Sugere próximos passos

## Pré-requisitos

Nenhum - este é o primeiro comando a executar.

## Próximos passos sugeridos

- `/discovery` - Iniciar discovery de usuários
- `/competitors` - Mapear concorrentes

# Cenários BDD Gerados

## Funcionalidade: Adicionar produtos ao carrinho de compras

### Cenário 1: Adicionar um produto com sucesso
    Dado que o usuário visualiza a página de um produto
    Quando o usuário clica no botão "Adicionar ao carrinho"
    Então o produto é adicionado ao carrinho de compras
    E o sistema exibe uma mensagem de confirmação

### Cenário 2: Tentar adicionar um produto sem estoque
    Dado que o usuário visualiza a página de um produto sem estoque
    Quando o usuário clica no botão "Adicionar ao carrinho"
    Então o sistema exibe uma mensagem de erro informando que o produto está indisponível
    E o produto não é adicionado ao carrinho de compras

### Cenário 3: Adicionar um produto com quantidade inválida
    Dado que o usuário visualiza a página de um produto
    E o usuário seleciona uma quantidade inválida (por exemplo, 0)
    Quando o usuário clica no botão "Adicionar ao carrinho"
    Então o sistema exibe uma mensagem de erro informando que a quantidade deve ser maior que zero
    E o produto não é adicionado ao carrinho de compras

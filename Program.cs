using GeradorDeDocumentosLegislativos.Models;
bool showMenu = true;
string? userOption;

while (showMenu)
{

    Console.WriteLine("Escolha o número da opção desejada:");
    Console.WriteLine("1 - Projetos de Lei");
    Console.WriteLine("2 - Proposições do Legislativo");
    Console.WriteLine("3 - Matérias auxiliares");
    Console.WriteLine("4 - Proposições Não Normativas");
    Console.WriteLine("5 - Documentos de Sessão");
    Console.WriteLine("6 - Votos e Manifestações");
    Console.WriteLine("7 - Títulos e Honrarias");
    Console.WriteLine("8 - Configurações");
    Console.WriteLine("0 - Sair");

    userOption = Console.ReadLine();

    switch (userOption)
    {
        case "1":
            Console.WriteLine("Projetos de Lei");
            break;

        case "2":
            Console.WriteLine("Proposições do Legislativo");
            break;

        case "3":
            Console.WriteLine("Matérias auxiliares");
            break;

        case "4":
            Console.WriteLine("Proposições Não Normativas");
            DateTime todaysDate = DateTime.Now;
            string dateForImpression = todaysDate.ToString("d 'de' MMMM 'de' yyyy");

            Indicacao indicacaoTeste = new Indicacao();

            Console.WriteLine("Digite o número da indicação:");
            indicacaoTeste.PropositionNumber = Convert.ToInt32(Console.ReadLine());
            indicacaoTeste.PrintPdf();
            break;

        case "5":
            Console.WriteLine("Documentos de Sessão");
            break;

        case "6":
            Console.WriteLine("Votos e Manifestações");
            break;

        case "7":
            Console.WriteLine("Títulos e Honrarias");
            break;

        case "8":
            Console.WriteLine("Configurações");
            break;

        case "0":
            showMenu = false;
            break;
    }

}

Console.WriteLine("Programa encerrado!");




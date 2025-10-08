using GeradorDeDocumentosLegislativos.Models;

DateTime todaysDate = DateTime.Now;
string dateForImpression = todaysDate.ToString("d 'de' MMMM 'de' yyyy");

Indicacao indicacaoTeste = new Indicacao();

Console.WriteLine("Digite o número da indicação:");
indicacaoTeste.PropositionNumber = Convert.ToInt32(Console.ReadLine());
indicacaoTeste.PrintPdf();
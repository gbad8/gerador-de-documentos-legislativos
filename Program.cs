using GeradorDeDocumentosLegislativos.Models;

DateTime todaysDate = DateTime.Now;
string dateForImpression = todaysDate.ToString("d 'de' MMMM 'de' yyyy");

Indicacao indicacaoTeste = new Indicacao();
indicacaoTeste.PropositionNumber = 63;
indicacaoTeste.PrintPdf();
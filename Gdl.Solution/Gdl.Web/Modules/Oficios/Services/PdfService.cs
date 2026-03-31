using PuppeteerSharp;
using PuppeteerSharp.Media;

namespace Gdl.Web.Modules.Oficios.Services
{
    public class PdfService : IPdfService
    {
        public async Task<byte[]> GeneratePdfFromHtmlAsync(string htmlContent)
        {
            var browserFetcher = new BrowserFetcher();
            await browserFetcher.DownloadAsync();

            using var browser = await Puppeteer.LaunchAsync(new LaunchOptions
            {
                Headless = true,
                Args = new[] { "--no-sandbox", "--disable-setuid-sandbox" }
            });

            using var page = await browser.NewPageAsync();
            await page.SetContentAsync(htmlContent);

            return await page.PdfDataAsync(new PdfOptions
            {
                Format = PaperFormat.A4,
                PrintBackground = true,
                PreferCSSPageSize = true,
                MarginOptions = new MarginOptions
                {
                    Top = "0cm",
                    Bottom = "0cm",
                    Left = "0cm",
                    Right = "0cm"
                }
            });
        }
    }
}

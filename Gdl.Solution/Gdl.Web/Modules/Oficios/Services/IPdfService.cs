namespace Gdl.Web.Modules.Oficios.Services
{
    public interface IPdfService
    {
        Task<byte[]> GeneratePdfFromHtmlAsync(string htmlContent);
    }
}

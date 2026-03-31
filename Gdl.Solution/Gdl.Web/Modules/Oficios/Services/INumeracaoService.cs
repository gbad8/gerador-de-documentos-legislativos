namespace Gdl.Web.Modules.Oficios.Services
{
    public interface INumeracaoService
    {
        Task<string> GerarProximoNumeroAsync(int? orgaoId, int autorId);
    }
}

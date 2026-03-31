using Microsoft.EntityFrameworkCore;
using Gdl.Web.Infrastructure.Data;
using Gdl.Web.Infrastructure.Multitenancy;
using Gdl.Web.Modules.Oficios.Models;

namespace Gdl.Web.Modules.Oficios.Services
{
    public class NumeracaoService : INumeracaoService
    {
        private readonly AppDbContext _context;
        private readonly ITenantService _tenantService;

        public NumeracaoService(AppDbContext context, ITenantService tenantService)
        {
            _context = context;
            _tenantService = tenantService;
        }

        public async Task<string> GerarProximoNumeroAsync(int? orgaoId, int autorId)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var anoAtual = DateTime.UtcNow.Year;

            // Strategy: transaction locked to serialize numbering across cluster if needed
            using var transaction = await _context.Database.BeginTransactionAsync(System.Data.IsolationLevel.Serializable);

            var num = await _context.Set<Numeracao>()
                .FirstOrDefaultAsync(n => n.CamaraId == camaraId && n.OrgaoId == orgaoId && n.AutorId == autorId && n.Ano == anoAtual);

            if (num == null)
            {
                num = new Numeracao
                {
                    CamaraId = camaraId,
                    OrgaoId = orgaoId,
                    AutorId = autorId,
                    Ano = anoAtual,
                    UltimoNumero = 0
                };
                _context.Set<Numeracao>().Add(num);
            }

            num.UltimoNumero++;
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            return $"{num.UltimoNumero.ToString("D3")}/{anoAtual}";
        }
    }
}

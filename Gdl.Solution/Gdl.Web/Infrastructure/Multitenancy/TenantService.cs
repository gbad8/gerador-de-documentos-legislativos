using Microsoft.AspNetCore.Http;
using System.Security.Claims;

namespace Gdl.Web.Infrastructure.Multitenancy
{
    public class TenantService : ITenantService
    {
        private readonly IHttpContextAccessor _httpContextAccessor;

        public TenantService(IHttpContextAccessor httpContextAccessor)
        {
            _httpContextAccessor = httpContextAccessor;
        }

        public int CurrentCamaraId
        {
            get
            {
                var user = _httpContextAccessor.HttpContext?.User;
                if (user?.Identity?.IsAuthenticated == true)
                {
                    var claim = user.FindFirst("CamaraId");
                    if (claim != null && int.TryParse(claim.Value, out var camaraId))
                    {
                        return camaraId;
                    }
                }

                return 0;
            }
        }
    }
}

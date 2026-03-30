using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Modules.Camaras.Models;
using Gdl.Web.Modules.Identity.Models;
using Gdl.Web.Modules.Orgaos.Models;
using Gdl.Web.Infrastructure.Multitenancy;

namespace Gdl.Web.Infrastructure.Data
{
    public class AppDbContext : IdentityDbContext<ApplicationUser>
    {
        private readonly ITenantService _tenantService;

        public AppDbContext(
            DbContextOptions<AppDbContext> options,
            ITenantService tenantService) : base(options)
        {
            _tenantService = tenantService;
        }

        public DbSet<Camara> Camaras => Set<Camara>();
        public DbSet<Orgao> Orgaos => Set<Orgao>();

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);

            // Nomes de tabelas simplificados do Identity
            builder.Entity<ApplicationUser>().ToTable("Usuarios");
            builder.Entity<IdentityRole>().ToTable("Roles");
            builder.Entity<IdentityUserRole<string>>().ToTable("UsuarioRoles");
            builder.Entity<IdentityUserClaim<string>>().ToTable("UsuarioClaims");
            builder.Entity<IdentityUserLogin<string>>().ToTable("UsuarioLogins");
            builder.Entity<IdentityRoleClaim<string>>().ToTable("RoleClaims");
            builder.Entity<IdentityUserToken<string>>().ToTable("UsuarioTokens");

            // -------- Multi-Tenancy (Local/Global Query Filter) --------

            // Ignorar tenant filtrado quando CamaraId for 0 (rotinas super admin/sistemas)
            builder.Entity<ApplicationUser>()
                .HasQueryFilter(u => _tenantService.CurrentCamaraId == 0 || u.CamaraId == _tenantService.CurrentCamaraId);

            builder.Entity<Orgao>()
                .HasQueryFilter(o => _tenantService.CurrentCamaraId == 0 || o.CamaraId == _tenantService.CurrentCamaraId);

            // Relacionamento Usuario -> Camara
            builder.Entity<ApplicationUser>()
                .HasOne(u => u.Camara)
                .WithMany()
                .HasForeignKey(u => u.CamaraId)
                .OnDelete(DeleteBehavior.Restrict);
        }
    }
}

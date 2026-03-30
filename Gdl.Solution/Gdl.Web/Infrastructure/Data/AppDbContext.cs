using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Modules.Camaras.Models;
using Gdl.Web.Modules.Identity.Models;
using Gdl.Web.Modules.Orgaos.Models;
using Gdl.Web.Modules.Autores.Models;
using Gdl.Web.Modules.Autores.Models.Enums;
using Gdl.Web.Modules.Oficios.Models;
using Gdl.Web.Modules.Oficios.Models.Enums;
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
        public DbSet<Autor> Autores => Set<Autor>();
        public DbSet<Oficio> Oficios => Set<Oficio>();
        public DbSet<Numeracao> Numeracoes => Set<Numeracao>();

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

            builder.Entity<Autor>()
                .HasQueryFilter(a => _tenantService.CurrentCamaraId == 0 || a.CamaraId == _tenantService.CurrentCamaraId);

            // Mapeamento compatível do C# Enum para Varchar(3) no Banco legado do Django (1S e 2S)
            builder.Entity<Autor>()
                .Property(a => a.Cargo)
                .HasConversion(
                    v => v == CargoAutor.S1 ? "1S" : (v == CargoAutor.S2 ? "2S" : v.ToString()),
                    v => v == "1S" ? CargoAutor.S1 : (v == "2S" ? CargoAutor.S2 : Enum.Parse<CargoAutor>(v)))
                .HasMaxLength(3);

            builder.Entity<Oficio>()
                .HasQueryFilter(o => _tenantService.CurrentCamaraId == 0 || o.CamaraId == _tenantService.CurrentCamaraId);

            builder.Entity<Numeracao>()
                .HasQueryFilter(n => _tenantService.CurrentCamaraId == 0 || n.CamaraId == _tenantService.CurrentCamaraId);

            // Mapeamento StatusOficio para refletir strings minúsculas como no Django
            builder.Entity<Oficio>()
                .Property(o => o.Status)
                .HasConversion(
                    v => v.ToString().ToLower(),
                    v => (StatusOficio)Enum.Parse(typeof(StatusOficio), v, true))
                .HasMaxLength(20);

            // Para evitar ciclos de cascata de delete que o SQL Server/Postgres reclamam, deixamos protect onde aplicável
            builder.Entity<Oficio>()
                .HasOne(o => o.Autor)
                .WithMany()
                .HasForeignKey(o => o.AutorId)
                .OnDelete(DeleteBehavior.Restrict);

            // Relacionamento Many-to-Many Coautores
            builder.Entity<Oficio>()
                .HasMany(o => o.Coautores)
                .WithMany()
                .UsingEntity("OficioCoautores");

            // Relacionamento Usuario -> Camara
            builder.Entity<ApplicationUser>()
                .HasOne(u => u.Camara)
                .WithMany()
                .HasForeignKey(u => u.CamaraId)
                .OnDelete(DeleteBehavior.Restrict);
        }
    }
}

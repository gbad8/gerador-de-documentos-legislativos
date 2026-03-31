using Microsoft.AspNetCore.Identity;
using Gdl.Web.Modules.Identity.Models;
using Gdl.Web.Modules.Camaras.Models;
using Gdl.Web.Modules.Camaras.Models.Enums;
using Gdl.Web.Modules.Identity.Models.Enums;

namespace Gdl.Web.Infrastructure.Data
{
    public static class DbSeeder
    {
        public static async Task SeedAsync(IServiceProvider serviceProvider)
        {
            var context = serviceProvider.GetRequiredService<AppDbContext>();
            var userManager = serviceProvider.GetRequiredService<UserManager<ApplicationUser>>();

            context.Database.EnsureCreated();

            // Garantir que exista uma Câmara
            var camara = context.Camaras.FirstOrDefault();
            if (camara == null)
            {
                camara = new Camara
                {
                    Nome = "Câmara Municipal de Teste",
                    Cidade = "Cidade Modelo",
                    Estado = EstadoCamara.SP,
                    Cnpj = "00.000.000/0001-00"
                };
                context.Camaras.Add(camara);
                await context.SaveChangesAsync();
            }

            // Garantir usuário admin
            if (!userManager.Users.Any())
            {
                var adminUser = new ApplicationUser
                {
                    UserName = "admin",
                    Nome = "Administrador do Sistema",
                    Email = "admin@gdl.com",
                    CamaraId = camara.Id,
                    Role = RoleUsuario.ADM,
                    Cargo = CargoUsuario.PA
                };

                await userManager.CreateAsync(adminUser, "Senha@123");
            }
        }
    }
}

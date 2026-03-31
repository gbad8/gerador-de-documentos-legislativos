using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Identity;
using Gdl.Web.Infrastructure.Data;
using Gdl.Web.Infrastructure.Multitenancy;
using Gdl.Web.Modules.Identity.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews()
    .AddRazorOptions(options =>
    {
        options.ViewLocationFormats.Clear();
        options.ViewLocationFormats.Add("/Modules/{1}/Views/{0}.cshtml");
        options.ViewLocationFormats.Add("/Modules/Shared/Views/{0}.cshtml");
        options.ViewLocationFormats.Add("/Views/{1}/{0}.cshtml");
        options.ViewLocationFormats.Add("/Views/Shared/{0}.cshtml");
    });

// --- GDL Configs & Injections ---
// 1. Acesso ao HttpContext para leitura do Tenant (CamaraId) logado
builder.Services.AddHttpContextAccessor();

// 2. Serviço de Tenant para o Global Query Filter
builder.Services.AddScoped<ITenantService, TenantService>();
builder.Services.AddScoped<Gdl.Web.Modules.Oficios.Services.INumeracaoService, Gdl.Web.Modules.Oficios.Services.NumeracaoService>();
builder.Services.AddScoped<Gdl.Web.Infrastructure.Services.IViewRenderService, Gdl.Web.Infrastructure.Services.ViewRenderService>();
builder.Services.AddScoped<Gdl.Web.Modules.Oficios.Services.IPdfService, Gdl.Web.Modules.Oficios.Services.PdfService>();

// 3. Configuração do EF Core e PostgreSQL
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// 4. Configuração do Identity
builder.Services.AddIdentity<ApplicationUser, IdentityRole>(options => 
{
    options.SignIn.RequireConfirmedAccount = false;
})
.AddEntityFrameworkStores<AppDbContext>()
.AddDefaultTokenProviders();
// --------------------------------

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await Gdl.Web.Infrastructure.Data.DbSeeder.SeedAsync(scope.ServiceProvider);
}

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseRouting();

// Middleware de Autenticação obrigatório antes do de Autorização
app.UseAuthentication(); 
app.UseAuthorization();

app.MapStaticAssets();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}")
    .WithStaticAssets();

app.Run();

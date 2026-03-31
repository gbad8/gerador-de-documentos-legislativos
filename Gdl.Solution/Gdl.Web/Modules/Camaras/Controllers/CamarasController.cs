using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Gdl.Web.Infrastructure.Data;
using Gdl.Web.Infrastructure.Multitenancy;
using Gdl.Web.Modules.Camaras.Models;

namespace Gdl.Web.Modules.Camaras.Controllers
{
    [Authorize]
    public class CamarasController : Controller
    {
        private readonly AppDbContext _context;
        private readonly ITenantService _tenantService;

        public CamarasController(AppDbContext context, ITenantService tenantService)
        {
            _context = context;
            _tenantService = tenantService;
        }

        // Dashboard de Configurações
        public IActionResult Index()
        {
            return View();
        }

        [HttpGet]
        public async Task<IActionResult> Edit()
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var camara = await _context.Camaras.FindAsync(camaraId);
            if (camara == null) return NotFound();

            var model = new CamaraViewModel
            {
                Id = camara.Id,
                Nome = camara.Nome,
                Cidade = camara.Cidade,
                Estado = camara.Estado,
                Cnpj = camara.Cnpj,
                Telefone = camara.Telefone,
                Email = camara.Email,
                Cep = camara.Cep,
                Endereco = camara.Endereco,
                LogomarcaBase64 = camara.LogomarcaBase64
            };

            return View(model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(CamaraViewModel model)
        {
            if (model.Id != _tenantService.CurrentCamaraId) return Unauthorized();

            if (ModelState.IsValid)
            {
                var camara = await _context.Camaras.FindAsync(model.Id);
                if (camara == null) return NotFound();

                camara.Nome = model.Nome!;
                camara.Cidade = model.Cidade ?? string.Empty;
                camara.Estado = model.Estado;
                camara.Cnpj = model.Cnpj!;
                camara.Telefone = model.Telefone ?? string.Empty;
                camara.Email = model.Email ?? string.Empty;
                camara.Cep = model.Cep ?? string.Empty;
                camara.Endereco = model.Endereco!;

                if (model.UploadLogomarca != null && model.UploadLogomarca.Length > 0)
                {
                    using (var ms = new MemoryStream())
                    {
                        await model.UploadLogomarca.CopyToAsync(ms);
                        camara.Logomarca = ms.ToArray();
                    }
                }

                _context.Update(camara);
                await _context.SaveChangesAsync();
                
                TempData["Success"] = "Dados da Câmara atualizados com sucesso!";
                return RedirectToAction(nameof(Index));
            }

            return View(model);
        }
    }
}

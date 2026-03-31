using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Infrastructure.Data;
using Gdl.Web.Infrastructure.Multitenancy;
using Gdl.Web.Modules.Autores.Models;

namespace Gdl.Web.Modules.Autores.Controllers
{
    [Authorize]
    public class AutoresController : Controller
    {
        private readonly AppDbContext _context;
        private readonly ITenantService _tenantService;

        public AutoresController(AppDbContext context, ITenantService tenantService)
        {
            _context = context;
            _tenantService = tenantService;
        }

        public IActionResult Index()
        {
            return View();
        }

        public async Task<IActionResult> List()
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var autores = await _context.Autores
                .Where(a => a.CamaraId == camaraId)
                .OrderBy(a => a.Nome)
                .ToListAsync();

            return PartialView("_List", autores);
        }

        [HttpGet]
        public IActionResult Create()
        {
            var model = new AutorViewModel();
            return PartialView("_FormModal", model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(AutorViewModel model)
        {
            if (ModelState.IsValid && model.Cargo.HasValue)
            {
                var autor = new Autor
                {
                    Nome = model.Nome,
                    Cargo = model.Cargo.Value,
                    CamaraId = _tenantService.CurrentCamaraId
                };

                _context.Autores.Add(autor);
                await _context.SaveChangesAsync();

                Response.Headers.Append("HX-Trigger", "autoresChanged");
                return Content("");
            }
            return PartialView("_FormModal", model);
        }

        [HttpGet]
        public async Task<IActionResult> Edit(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var autor = await _context.Autores.FirstOrDefaultAsync(a => a.Id == id && a.CamaraId == camaraId);
            if (autor == null) return NotFound();

            var model = new AutorViewModel
            {
                Id = autor.Id,
                Nome = autor.Nome,
                Cargo = autor.Cargo
            };

            return PartialView("_FormModal", model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(AutorViewModel model)
        {
            if (ModelState.IsValid && model.Cargo.HasValue)
            {
                var camaraId = _tenantService.CurrentCamaraId;
                var autor = await _context.Autores.FirstOrDefaultAsync(a => a.Id == model.Id && a.CamaraId == camaraId);
                if (autor == null) return NotFound();

                autor.Nome = model.Nome;
                autor.Cargo = model.Cargo.Value;

                await _context.SaveChangesAsync();

                Response.Headers.Append("HX-Trigger", "autoresChanged");
                return Content("");
            }
            return PartialView("_FormModal", model);
        }

        [HttpGet]
        public async Task<IActionResult> Delete(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var autor = await _context.Autores.FirstOrDefaultAsync(a => a.Id == id && a.CamaraId == camaraId);
            if (autor == null) return NotFound();

            return PartialView("_DeleteModal", autor);
        }

        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var autor = await _context.Autores.FirstOrDefaultAsync(a => a.Id == id && a.CamaraId == camaraId);
            if (autor != null)
            {
                _context.Autores.Remove(autor);
                await _context.SaveChangesAsync();
            }

            Response.Headers.Append("HX-Trigger", "autoresChanged");
            return Content("");
        }
    }
}

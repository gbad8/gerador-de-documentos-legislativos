using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Infrastructure.Data;
using Gdl.Web.Infrastructure.Multitenancy;
using Gdl.Web.Modules.Orgaos.Models;

namespace Gdl.Web.Modules.Orgaos.Controllers
{
    [Authorize]
    public class OrgaosController : Controller
    {
        private readonly AppDbContext _context;
        private readonly ITenantService _tenantService;

        public OrgaosController(AppDbContext context, ITenantService tenantService)
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
            var orgaos = await _context.Orgaos
                .Where(o => o.CamaraId == camaraId)
                .OrderBy(o => o.Nome)
                .ToListAsync();

            return PartialView("_List", orgaos);
        }

        [HttpGet]
        public IActionResult Create()
        {
            var model = new OrgaoViewModel();
            return PartialView("_FormModal", model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(OrgaoViewModel model)
        {
            if (ModelState.IsValid)
            {
                var camaraId = _tenantService.CurrentCamaraId;
                
                var existe = await _context.Orgaos.AnyAsync(o => o.Nome.ToLower() == model.Nome.ToLower() && o.CamaraId == camaraId);
                if (existe)
                {
                    ModelState.AddModelError("Nome", "Já existe um órgão com este nome.");
                    return PartialView("_FormModal", model);
                }

                var orgao = new Orgao
                {
                    Nome = model.Nome,
                    Abreviatura = model.Abreviatura,
                    CamaraId = camaraId
                };

                _context.Orgaos.Add(orgao);
                await _context.SaveChangesAsync();

                Response.Headers.Append("HX-Trigger", "orgaosChanged");
                return Content("");
            }
            return PartialView("_FormModal", model);
        }

        [HttpGet]
        public async Task<IActionResult> Edit(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var orgao = await _context.Orgaos.FirstOrDefaultAsync(o => o.Id == id && o.CamaraId == camaraId);
            if (orgao == null) return NotFound();

            var model = new OrgaoViewModel
            {
                Id = orgao.Id,
                Nome = orgao.Nome,
                Abreviatura = orgao.Abreviatura
            };

            return PartialView("_FormModal", model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(OrgaoViewModel model)
        {
            if (ModelState.IsValid)
            {
                var camaraId = _tenantService.CurrentCamaraId;
                var orgao = await _context.Orgaos.FirstOrDefaultAsync(o => o.Id == model.Id && o.CamaraId == camaraId);
                if (orgao == null) return NotFound();

                var existe = await _context.Orgaos.AnyAsync(o => o.Nome.ToLower() == model.Nome.ToLower() && o.CamaraId == camaraId && o.Id != model.Id);
                if (existe)
                {
                    ModelState.AddModelError("Nome", "Já existe um órgão com este nome.");
                    return PartialView("_FormModal", model);
                }

                orgao.Nome = model.Nome;
                orgao.Abreviatura = model.Abreviatura;

                await _context.SaveChangesAsync();

                Response.Headers.Append("HX-Trigger", "orgaosChanged");
                return Content("");
            }
            return PartialView("_FormModal", model);
        }

        [HttpGet]
        public async Task<IActionResult> Delete(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var orgao = await _context.Orgaos.FirstOrDefaultAsync(o => o.Id == id && o.CamaraId == camaraId);
            if (orgao == null) return NotFound();

            return PartialView("_DeleteModal", orgao);
        }

        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var orgao = await _context.Orgaos.FirstOrDefaultAsync(o => o.Id == id && o.CamaraId == camaraId);
            if (orgao != null)
            {
                _context.Orgaos.Remove(orgao);
                await _context.SaveChangesAsync();
            }

            Response.Headers.Append("HX-Trigger", "orgaosChanged");
            return Content("");
        }
    }
}

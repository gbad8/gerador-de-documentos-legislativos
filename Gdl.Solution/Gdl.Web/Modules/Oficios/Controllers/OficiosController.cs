using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Infrastructure.Data;
using Gdl.Web.Infrastructure.Multitenancy;
using Gdl.Web.Modules.Oficios.Models;
using Gdl.Web.Modules.Oficios.Models.Enums;
using Gdl.Web.Modules.Oficios.Services;

namespace Gdl.Web.Modules.Oficios.Controllers
{
    [Authorize]
    public class OficiosController : Controller
    {
        private readonly AppDbContext _context;
        private readonly ITenantService _tenantService;
        private readonly INumeracaoService _numeracaoService;

        public OficiosController(AppDbContext context, ITenantService tenantService, INumeracaoService numeracaoService)
        {
            _context = context;
            _tenantService = tenantService;
            _numeracaoService = numeracaoService;
        }

        public async Task<IActionResult> Index()
        {
            return View();
        }

        public async Task<IActionResult> Search(string? q)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var query = _context.Oficios
                .Include(o => o.Autor)
                .Include(o => o.Orgao)
                .Where(o => o.CamaraId == camaraId);

            if (!string.IsNullOrWhiteSpace(q))
            {
                query = query.Where(o => o.Assunto.ToLower().Contains(q.ToLower()));
            }

            var oficios = await query.OrderByDescending(o => o.CriadoEm).ToListAsync();

            return PartialView("_SearchResults", oficios);
        }

        [HttpGet]
        public async Task<IActionResult> Create()
        {
            await PopulateViewBagsAsync();
            return View(new OficioViewModel { Data = DateTime.Today });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(OficioViewModel model)
        {
            if (ModelState.IsValid)
            {
                var camaraId = _tenantService.CurrentCamaraId;
                var numero = await _numeracaoService.GerarProximoNumeroAsync(model.OrgaoId, model.AutorId);

                var oficio = new Oficio
                {
                    CamaraId = camaraId,
                    OrgaoId = model.OrgaoId,
                    AutorId = model.AutorId,
                    Numero = numero,
                    Assunto = model.Assunto,
                    Corpo = model.Corpo ?? string.Empty,
                    Data = model.Data,
                    Status = StatusOficio.Rascunho,
                    EConjunto = model.EConjunto,
                    DestinatarioNome = model.DestinatarioNome ?? string.Empty,
                    DestinatarioCargo = model.DestinatarioCargo,
                    DestinatarioOrgao = model.DestinatarioOrgao,
                    DestinatarioEndereco = model.DestinatarioEndereco,
                    DestinatarioPronome = model.DestinatarioPronome ?? "Ao Senhor(a)",
                    CriadoEm = DateTime.UtcNow,
                    AtualizadoEm = DateTime.UtcNow
                };

                if (model.EConjunto && model.CoautoresIds.Any())
                {
                    var coautores = await _context.Autores.Where(a => model.CoautoresIds.Contains(a.Id)).ToListAsync();
                    oficio.Coautores = coautores;
                }

                _context.Oficios.Add(oficio);
                await _context.SaveChangesAsync();

                return RedirectToAction(nameof(Preview), new { id = oficio.Id });
            }

            await PopulateViewBagsAsync();
            return View(model);
        }

        [HttpGet]
        public async Task<IActionResult> Edit(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var oficio = await _context.Oficios
                .Include(o => o.Coautores)
                .FirstOrDefaultAsync(o => o.Id == id && o.CamaraId == camaraId);

            if (oficio == null) return NotFound();

            var model = new OficioViewModel
            {
                Id = oficio.Id,
                Numero = oficio.Numero,
                Assunto = oficio.Assunto,
                Corpo = oficio.Corpo,
                Data = oficio.Data,
                EConjunto = oficio.EConjunto,
                DestinatarioNome = oficio.DestinatarioNome,
                DestinatarioCargo = oficio.DestinatarioCargo,
                DestinatarioOrgao = oficio.DestinatarioOrgao,
                DestinatarioEndereco = oficio.DestinatarioEndereco,
                DestinatarioPronome = oficio.DestinatarioPronome,
                AutorId = oficio.AutorId,
                OrgaoId = oficio.OrgaoId,
                CoautoresIds = oficio.Coautores.Select(c => c.Id).ToList()
            };

            await PopulateViewBagsAsync();
            return View(model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(OficioViewModel model)
        {
            if (ModelState.IsValid)
            {
                var camaraId = _tenantService.CurrentCamaraId;
                var oficio = await _context.Oficios
                    .Include(o => o.Coautores)
                    .FirstOrDefaultAsync(o => o.Id == model.Id && o.CamaraId == camaraId);

                if (oficio == null) return NotFound();

                oficio.Assunto = model.Assunto;
                oficio.Corpo = model.Corpo ?? string.Empty;
                oficio.Data = model.Data;
                oficio.EConjunto = model.EConjunto;
                oficio.DestinatarioNome = model.DestinatarioNome ?? string.Empty;
                oficio.DestinatarioCargo = model.DestinatarioCargo;
                oficio.DestinatarioOrgao = model.DestinatarioOrgao;
                oficio.DestinatarioEndereco = model.DestinatarioEndereco;
                oficio.DestinatarioPronome = model.DestinatarioPronome ?? "Ao Senhor(a)";
                oficio.AutorId = model.AutorId;
                oficio.OrgaoId = model.OrgaoId;
                oficio.AtualizadoEm = DateTime.UtcNow;

                oficio.Status = StatusOficio.Modificado;

                oficio.Coautores.Clear();
                if (model.EConjunto && model.CoautoresIds.Any())
                {
                    var coautores = await _context.Autores.Where(a => model.CoautoresIds.Contains(a.Id)).ToListAsync();
                    oficio.Coautores = coautores;
                }

                await _context.SaveChangesAsync();
                return RedirectToAction(nameof(Preview), new { id = oficio.Id });
            }

            await PopulateViewBagsAsync();
            return View(model);
        }

        public async Task<IActionResult> Preview(int id)
        {
            var camaraId = _tenantService.CurrentCamaraId;
            var oficio = await _context.Oficios
                .Include(o => o.Autor)
                .Include(o => o.Orgao)
                .Include(o => o.Camara)
                .Include(o => o.Coautores)
                .FirstOrDefaultAsync(o => o.Id == id && o.CamaraId == camaraId);

            if (oficio == null) return NotFound();

            if (Request.Headers["HX-Request"] == "true")
            {
                return PartialView("_Preview", oficio);
            }

            return View("Detail", oficio);
        }

        private async Task PopulateViewBagsAsync()
        {
            var camaraId = _tenantService.CurrentCamaraId;
            ViewBag.Autores = await _context.Autores.Where(a => a.CamaraId == camaraId).OrderBy(a => a.Nome).ToListAsync();
            ViewBag.Orgaos = await _context.Orgaos.Where(o => o.CamaraId == camaraId).OrderBy(o => o.Nome).ToListAsync();
        }
    }
}

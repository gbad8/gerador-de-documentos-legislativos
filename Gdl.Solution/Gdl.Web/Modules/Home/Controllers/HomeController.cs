using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Gdl.Web.Infrastructure.Data;
using Gdl.Web.Modules.Admin.Models;

namespace Gdl.Web.Modules.Home.Controllers;

[Authorize]
public class HomeController : Controller
{
    private readonly AppDbContext _dbContext;

    public HomeController(AppDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    [HttpPost]
    [AllowAnonymous]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> SolicitarAcesso(SolicitacaoAcesso solicitacao)
    {
        if (ModelState.IsValid)
        {
            _dbContext.SolicitacoesAcesso.Add(solicitacao);
            await _dbContext.SaveChangesAsync();
            TempData["SuccessMessage"] = "Sua solicitação foi enviada! Nossa equipe entrará em contato em breve.";
        }
        else
        {
            TempData["ErrorMessage"] = "Preencha todos os campos corretamente.";
        }
        return RedirectToAction("Index");
    }

    [AllowAnonymous]
    public IActionResult Index()
    {
        if (User.Identity?.IsAuthenticated == true)
        {
            return RedirectToAction("Dashboard");
        }
        return View();
    }

    public IActionResult Dashboard()
    {
        return View();
    }

    [HttpGet]
    public IActionResult Configuracoes()
    {
        return View();
    }

    public IActionResult Privacy()
    {
        return View();
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View();
    }
}

using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Identity.Models.Enums
{
    public enum RoleUsuario
    {
        [Display(Name = "Administrador")]
        ADM,
        [Display(Name = "Operador")]
        OPR
    }
}

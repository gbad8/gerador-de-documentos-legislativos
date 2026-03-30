using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Identity.Models.Enums
{
    public enum CargoUsuario
    {
        [Display(Name = "Parlamentar")]
        PA,
        [Display(Name = "Assessor Parlamentar")]
        AP,
        [Display(Name = "Assessor Jurídico")]
        AJ,
        [Display(Name = "Assessor Contábil")]
        AC
    }
}

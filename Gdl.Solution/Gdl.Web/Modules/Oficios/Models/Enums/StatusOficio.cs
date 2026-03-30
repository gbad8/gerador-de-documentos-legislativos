using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Oficios.Models.Enums
{
    public enum StatusOficio
    {
        [Display(Name = "Rascunho")] 
        Rascunho,
        [Display(Name = "Finalizado")] 
        Finalizado,
        [Display(Name = "Modificado")] 
        Modificado
    }
}

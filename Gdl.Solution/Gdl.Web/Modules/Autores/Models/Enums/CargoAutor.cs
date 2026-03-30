using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Autores.Models.Enums
{
    public enum CargoAutor
    {
        [Display(Name = "Presidente")] PR,
        [Display(Name = "Vice-Presidente")] VP,
        [Display(Name = "1º Secretário")] S1,
        [Display(Name = "2º Secretário")] S2,
        [Display(Name = "Vereador")] VER
    }
}

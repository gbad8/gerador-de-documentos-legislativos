using System.ComponentModel.DataAnnotations;
using Gdl.Web.Modules.Autores.Models.Enums;

namespace Gdl.Web.Modules.Autores.Models
{
    public class AutorViewModel
    {
        public int Id { get; set; }

        [Required(ErrorMessage = "O Nome Completo é obrigatório.")]
        [StringLength(100)]
        [Display(Name = "Nome Completo *")]
        public string Nome { get; set; } = string.Empty;

        [Required(ErrorMessage = "O Cargo / Função é obrigatório.")]
        [Display(Name = "Cargo / Função *")]
        public CargoAutor? Cargo { get; set; }
    }
}

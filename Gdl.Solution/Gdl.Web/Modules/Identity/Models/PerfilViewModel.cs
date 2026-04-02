using System.ComponentModel.DataAnnotations;
using Gdl.Web.Modules.Identity.Models.Enums;

namespace Gdl.Web.Modules.Identity.Models
{
    public class PerfilViewModel
    {
        [Required(ErrorMessage = "O nome de usuário é obrigatório.")]
        [Display(Name = "Nome de Usuário")]
        public string Username { get; set; } = string.Empty;

        [Required(ErrorMessage = "O e-mail é obrigatório.")]
        [EmailAddress(ErrorMessage = "E-mail inválido.")]
        [Display(Name = "E-mail")]
        public string Email { get; set; } = string.Empty;

        [Required(ErrorMessage = "O nome é obrigatório.")]
        [Display(Name = "Nome Completo")]
        public string Nome { get; set; } = string.Empty;

        [Required(ErrorMessage = "O cargo é obrigatório.")]
        [Display(Name = "Cargo")]
        public CargoUsuario Cargo { get; set; }
    }
}

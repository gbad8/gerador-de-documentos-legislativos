using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Identity.Models
{
    public class LoginViewModel
    {
        [Required(ErrorMessage = "O Usuário é obrigatório.")]
        public string Username { get; set; } = string.Empty;

        [Required(ErrorMessage = "A Senha é obrigatória.")]
        [DataType(DataType.Password)]
        public string Password { get; set; } = string.Empty;
    }
}

using Microsoft.AspNetCore.Identity;
using System.ComponentModel.DataAnnotations;
using Gdl.Web.Modules.Identity.Models.Enums;
using Gdl.Web.Modules.Camaras.Models;

namespace Gdl.Web.Modules.Identity.Models
{
    public class ApplicationUser : IdentityUser
    {
        public int CamaraId { get; set; }
        public Camara? Camara { get; set; }

        [Required]
        [MaxLength(200)]
        public string Nome { get; set; } = string.Empty;

        [Required]
        public RoleUsuario Role { get; set; } = RoleUsuario.OPR;

        [Required]
        public CargoUsuario Cargo { get; set; }
    }
}

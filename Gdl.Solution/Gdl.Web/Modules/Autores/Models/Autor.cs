using System.ComponentModel.DataAnnotations;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Modules.Camaras.Models;
using Gdl.Web.Modules.Autores.Models.Enums;

namespace Gdl.Web.Modules.Autores.Models
{
    [Index(nameof(CamaraId), nameof(Nome), nameof(Cargo), IsUnique = true)]
    public class Autor
    {
        public int Id { get; set; }

        public int CamaraId { get; set; }
        public Camara? Camara { get; set; }

        [Required]
        [MaxLength(200)]
        public string Nome { get; set; } = string.Empty;

        [Required]
        public CargoAutor Cargo { get; set; } = CargoAutor.VER;
    }
}

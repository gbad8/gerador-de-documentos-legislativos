using System.ComponentModel.DataAnnotations;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Modules.Camaras.Models;

namespace Gdl.Web.Modules.Orgaos.Models
{
    [Index(nameof(CamaraId), nameof(Nome), IsUnique = true)]
    public class Orgao
    {
        public int Id { get; set; }

        public int CamaraId { get; set; }
        public Camara? Camara { get; set; }

        [Required]
        [MaxLength(100)]
        public string Nome { get; set; } = string.Empty;

        [MaxLength(10)]
        public string? Abreviatura { get; set; }
    }
}

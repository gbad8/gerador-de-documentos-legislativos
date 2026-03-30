using System.ComponentModel.DataAnnotations;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Modules.Camaras.Models;
using Gdl.Web.Modules.Orgaos.Models;
using Gdl.Web.Modules.Autores.Models;

namespace Gdl.Web.Modules.Oficios.Models
{
    [Index(nameof(CamaraId), nameof(OrgaoId), nameof(AutorId), nameof(Ano), IsUnique = true)]
    public class Numeracao
    {
        public int Id { get; set; }

        public int CamaraId { get; set; }
        public Camara? Camara { get; set; }

        public int? OrgaoId { get; set; }
        public Orgao? Orgao { get; set; }

        public int AutorId { get; set; }
        public Autor? Autor { get; set; }

        [Required]
        public int Ano { get; set; }

        [Required]
        public int UltimoNumero { get; set; } = 0;
    }
}

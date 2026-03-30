using System.ComponentModel.DataAnnotations;
using Microsoft.EntityFrameworkCore;
using Gdl.Web.Modules.Camaras.Models;
using Gdl.Web.Modules.Orgaos.Models;
using Gdl.Web.Modules.Autores.Models;
using Gdl.Web.Modules.Oficios.Models.Enums;

namespace Gdl.Web.Modules.Oficios.Models
{
    [Index(nameof(CamaraId), nameof(CriadoEm), IsDescending = new[] { false, true })]
    [Index(nameof(CamaraId), nameof(OrgaoId))]
    [Index(nameof(CamaraId), nameof(AutorId))]
    [Index(nameof(CamaraId), nameof(Status))]
    public class Oficio
    {
        public int Id { get; set; }

        public int CamaraId { get; set; }
        public Camara? Camara { get; set; }

        public int? OrgaoId { get; set; }
        public Orgao? Orgao { get; set; }

        public int AutorId { get; set; }
        public Autor? Autor { get; set; }

        [Required]
        [MaxLength(10)]
        public string Numero { get; set; } = string.Empty;

        [Required]
        [MaxLength(500)]
        public string Assunto { get; set; } = string.Empty;

        [Required]
        public string Corpo { get; set; } = string.Empty;

        [Required]
        public DateTime Data { get; set; }

        [Required]
        public StatusOficio Status { get; set; } = StatusOficio.Rascunho;

        public bool EConjunto { get; set; }

        // Destinatário
        [Required]
        [MaxLength(200)]
        public string DestinatarioNome { get; set; } = string.Empty;

        [MaxLength(200)]
        public string? DestinatarioCargo { get; set; }

        [MaxLength(200)]
        public string? DestinatarioOrgao { get; set; }

        public string? DestinatarioEndereco { get; set; }

        [Required]
        [MaxLength(50)]
        public string DestinatarioPronome { get; set; } = string.Empty;

        public DateTime CriadoEm { get; set; }
        public DateTime AtualizadoEm { get; set; }

        // Coautores (Muitos-para-muitos)
        public ICollection<Autor> Coautores { get; set; } = new List<Autor>();
    }
}

using System.ComponentModel.DataAnnotations;
using Gdl.Web.Modules.Camaras.Models.Enums;

namespace Gdl.Web.Modules.Camaras.Models
{
    public class Camara
    {
        public int Id { get; set; }

        [Required]
        [MaxLength(100)]
        public string Nome { get; set; } = string.Empty;

        [Required]
        [MaxLength(100)]
        public string Cidade { get; set; } = string.Empty;

        [Required]
        public EstadoCamara Estado { get; set; }

        [Required]
        [MaxLength(18)]
        public string Cnpj { get; set; } = string.Empty;

        public string Endereco { get; set; } = string.Empty;

        [MaxLength(9)]
        [RegularExpression(@"^\d{5}-?\d{3}$", ErrorMessage = "O formato do CEP é inválido.")]
        public string Cep { get; set; } = string.Empty;

        [MaxLength(20)]
        [Phone(ErrorMessage = "O formato do telefone é inválido.")]
        public string Telefone { get; set; } = string.Empty;

        [EmailAddress]
        public string Email { get; set; } = string.Empty;

        public byte[]? Logomarca { get; set; }

        // Propriedades computadas (ReadOnly)
        public string? LogomarcaBase64 => Logomarca != null
            ? Convert.ToBase64String(Logomarca)
            : null;

        public string PreposicaoEstado
        {
            get
            {
                var de = new[] { EstadoCamara.AL, EstadoCamara.GO, EstadoCamara.MT, EstadoCamara.MS, EstadoCamara.MG, EstadoCamara.PE, EstadoCamara.SC, EstadoCamara.SP, EstadoCamara.SE };
                var da = new[] { EstadoCamara.BA, EstadoCamara.PB };

                if (de.Contains(Estado)) return "de";
                if (da.Contains(Estado)) return "da";
                return "do";
            }
        }
    }
}

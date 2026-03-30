using System.ComponentModel.DataAnnotations;

namespace Gdl.Web.Modules.Camaras.Models
{
    public class Camara
    {
        public int Id { get; set; }

        [Required]
        [MaxLength(200)]
        public string Nome { get; set; } = string.Empty;

        [Required]
        [MaxLength(200)]
        public string Cidade { get; set; } = string.Empty;

        [Required]
        [MaxLength(2)]
        public string Estado { get; set; } = string.Empty; // Poderia ser Enum, mas manteremos string conforme Django

        [Required]
        [MaxLength(18)]
        public string Cnpj { get; set; } = string.Empty;

        public string Endereco { get; set; } = string.Empty;

        [MaxLength(9)]
        public string Cep { get; set; } = string.Empty;

        [MaxLength(20)]
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
                var de = new[] { "AL", "GO", "MT", "MS", "MG", "PE", "SC", "SP", "SE" };
                var da = new[] { "BA", "PB" };

                if (de.Contains(Estado)) return "de";
                if (da.Contains(Estado)) return "da";
                return "do";
            }
        }
    }
}

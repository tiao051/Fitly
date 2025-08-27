namespace BodyAnalysisBackend.DTOs
{
    public class AnalyzeResult
    {
        public required string Status { get; set; }
        public required string BodyType { get; set; }
        public double Confidence { get; set; }

    }
}

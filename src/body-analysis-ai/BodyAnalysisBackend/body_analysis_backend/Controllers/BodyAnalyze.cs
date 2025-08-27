using BodyAnalysisBackend.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace BodyAnalysisBackend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class BodyAnalyze : ControllerBase
    {
        [HttpPost("analyze")]
        public async Task<IActionResult> Analyze([FromBody] AnalyzeRequest request)
        {
            if (string.IsNullOrEmpty(request.UrlImg))
            {
                return BadRequest("Image URL cannot be null or empty.");
            }

            // TODO: Call AI processing service here. Currently mocking the result.
            var result = new AnalyzeResult
            {
                Status = "Success",
                BodyType = "V-Taper",
                Confidence = 0.92
            };

            // Simulate delay
            await Task.Delay(300);

            return Ok(result);
        }
    }
}
